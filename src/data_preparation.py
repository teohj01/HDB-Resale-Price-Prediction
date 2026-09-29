# Standard library imports
import logging
import re
from typing import Any, Dict, Optional

# Related third-party imports
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler


class DataPreparation:
    """
    A class used to clean and preprocess HDB resale prices data.

    Coordinates for each address are geocoded beforehand (via the OneMap API in
    get_address_coords.py) and looked up from config['hdb_address'], so clean_data can take
    the raw resale transactions all the way to model-ready features:

    1. clean_data: raw resale transactions -> cleaned data with distances to the nearest
       school, MRT/LRT station and mall.
    2. preprocessor: ColumnTransformer to fit on the training set.

    Attributes:
    -----------
    config : Dict[str, Any]
        Configuration dictionary containing parameters for data cleaning and preprocessing.
    preprocessor : sklearn.compose.ColumnTransformer
        A preprocessor pipeline for transforming numerical, nominal, and ordinal features.
    """

    EARTH_RADIUS_M = 6371000

    def __init__(self, config: Dict[str, Any]):
        """
        Initializes the DataPreparation class with a configuration dictionary.

        Args:
        -----
        config (Dict[str, Any]): Configuration dictionary containing parameters for data cleaning and preprocessing.
        """
        self.config = config
        self.preprocessor = self._create_preprocessor()

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cleans the input DataFrame by performing several preprocessing steps.

        Args:
        -----
        df (pd.DataFrame): The input DataFrame containing the raw data.

        Returns:
        --------
        pd.DataFrame: The cleaned DataFrame, with distances to the nearest amenities.
        """
        logging.info("Starting data cleaning.")
        df.drop_duplicates(inplace=True)
        df["flat_type"] = df["flat_type"].replace("FOUR ROOM", "4 ROOM")
        df["lease_commence_date"] = df["lease_commence_date"].abs()
        df["storey_range"] = df["storey_range"].apply(self._convert_storey_range)
        df = self._fill_missing_names(df, "town_id", "town_name")
        df = self._fill_missing_names(df, "flatm_id", "flatm_name")
        df.drop(columns=["id", "town_id", "flatm_id"], inplace=True)
        df["year_month"] = pd.to_datetime(df["month"], format="%Y-%m")
        df["year"] = df["year_month"].dt.year
        df["month"] = df["year_month"].dt.month
        df.drop(columns=["year_month"], inplace=True)
        df["remaining_lease_months"] = df["remaining_lease"].apply(
            self._extract_lease_info
        )
        df["full_address"] = df["block"] + " " + df["street_name"]
        df.drop(columns=["remaining_lease", "block", "street_name"], inplace=True)
        df = self._add_coordinates(df)
        df = self._add_amenity_distances(df)
        df.drop(columns=["full_address", "latitude", "longitude"], inplace=True)
        logging.info("Data cleaning completed.")
        return df

    def _add_coordinates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Adds 'latitude' and 'longitude' for each address from the geocoded file in config['hdb_address'].

        Args:
        -----
        df (pd.DataFrame): The DataFrame with a 'full_address' column.

        Returns:
        --------
        pd.DataFrame: The DataFrame with 'latitude' and 'longitude' columns added.
        """
        address_coords = (
            pd.read_csv(self.config["hdb_address"])[
                ["full_address", "latitude", "longitude"]
            ]
            .drop_duplicates(subset="full_address")
        )
        df = df.merge(address_coords, on="full_address", how="left")
        missing = df["latitude"].isna().sum()
        if missing:
            logging.warning(f"{missing} row(s) have no coordinates for their address.")
        return df

    def _add_amenity_distances(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Adds the distance from each address to its nearest amenity (school, MRT/LRT station, mall).

        Amenity coordinate files are read from config['amenity_paths'], and each one produces a
        'distance_to_<amenity>' column.

        Args:
        -----
        df (pd.DataFrame): The DataFrame with 'latitude' and 'longitude' columns.

        Returns:
        --------
        pd.DataFrame: The DataFrame with distance features added.
        """
        for amenity, path in self.config["amenity_paths"].items():
            amenity_df = pd.read_csv(path)
            df[f"distance_to_{amenity}"] = self._distance_to_nearest(df, amenity_df)
        return df

    def _create_preprocessor(self) -> ColumnTransformer:
        """
        Creates a preprocessor pipeline for transforming numerical, nominal, and ordinal features.

        Returns:
        --------
        sklearn.compose.ColumnTransformer: A ColumnTransformer object for preprocessing the data.
        """
        numerical_transformer = Pipeline(steps=[("scaler", StandardScaler())])
        nominal_transformer = Pipeline(
            steps=[("onehot", OneHotEncoder(handle_unknown="ignore"))]
        )
        ordinal_transformer = Pipeline(
            steps=[
                (
                    "ordinal",
                    OrdinalEncoder(
                        categories=[self.config["flat_type_categories"]],
                        handle_unknown="use_encoded_value",
                        unknown_value=-1,
                    ),
                )
            ]
        )
        preprocessor = ColumnTransformer(
            transformers=[
                ("num", numerical_transformer, self.config["numerical_features"]),
                ("nom", nominal_transformer, self.config["nominal_features"]),
                ("ord", ordinal_transformer, self.config["ordinal_features"]),
                ("pass", "passthrough", self.config["passthrough_features"]),
            ],
            remainder="passthrough",
            n_jobs=-1,
        )
        return preprocessor

    @staticmethod
    def _convert_storey_range(storey_range: str) -> float:
        """
        Converts a storey range string into its average numerical value.

        Args:
        -----
        storey_range (str): A string representing a range of storeys, in the format 'XX TO YY'.

        Returns:
        --------
        float: The average value of the two storeys in the range.
        """
        range_values = storey_range.split(" TO ")
        return (int(range_values[0]) + int(range_values[1])) / 2

    @staticmethod
    def _fill_missing_names(
        df: pd.DataFrame, id_column: str, name_column: str
    ) -> pd.DataFrame:
        """
        Fills missing values in the 'name_column' using the 'id_column'.

        Args:
        -----
        df (pd.DataFrame): The DataFrame containing the columns to be filled.
        id_column (str): The name of the column containing the IDs.
        name_column (str): The name of the column containing the names to be filled.

        Returns:
        --------
        pd.DataFrame: The DataFrame with missing values in 'name_column' filled.
        """
        missing_names = df[name_column].isna()
        name_mapping = (
            df[[id_column, name_column]]
            .dropna()
            .drop_duplicates()
            .set_index(id_column)[name_column]
            .to_dict()
        )
        df.loc[missing_names, name_column] = df.loc[missing_names, id_column].map(
            name_mapping
        )
        return df

    @staticmethod
    def _extract_lease_info(lease_str: str) -> Optional[int]:
        """
        Converts lease information from a string format to total months.

        Args:
        -----
        lease_str (str): The remaining lease period as a string.

        Returns:
        --------
        Optional[int]: The total number of months, or None if the input is NaN.
        """
        if pd.isna(lease_str):
            return None
        years_match = re.search(r"(\d+)\s*years?", lease_str)
        months_match = re.search(r"(\d+)\s*months?", lease_str)
        number_match = re.match(r"^\d+$", lease_str.strip())
        if years_match:
            years = int(years_match.group(1))
        elif number_match:
            years = int(number_match.group(0))
        else:
            years = 0
        months = int(months_match.group(1)) if months_match else 0
        total_months = years * 12 + months
        return total_months

    @classmethod
    def _distance_to_nearest(
        cls, df: pd.DataFrame, amenity_df: pd.DataFrame
    ) -> pd.Series:
        """
        Calculates the great-circle distance from each address to its nearest amenity.

        Coordinates are converted to radians and indexed in a KD-tree; the chord distance
        to the nearest neighbour is then converted to an arc length on the Earth's surface.

        Args:
        -----
        df (pd.DataFrame): The DataFrame with 'latitude' and 'longitude' columns for each address.
        amenity_df (pd.DataFrame): The DataFrame with 'latitude' and 'longitude' columns for each amenity.

        Returns:
        --------
        pd.Series: The distance (in metres) to the nearest amenity, indexed like df.
        """
        property_rad = np.radians(df[["latitude", "longitude"]].to_numpy())
        amenity_rad = np.radians(amenity_df[["latitude", "longitude"]].to_numpy())
        tree = cKDTree(amenity_rad)
        chord_dist, _ = tree.query(property_rad, k=1)
        angular_dist = 2 * np.arcsin(chord_dist / 2)
        return pd.Series(angular_dist * cls.EARTH_RADIUS_M, index=df.index)
