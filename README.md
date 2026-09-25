# HDB Resale Price Prediction

## Project Description
This project implements a machine learning pipeline to predict HDB (Housing & Development Board) resale prices in Singapore. The pipeline includes data cleaning, preprocessing, model training, and evaluation. Multiple regression models are trained and compared to find the best performing one based on various metrics.

## Pre-requisites and Installation Instructions

### Requirements
- Anaconda or Miniconda
- Python 3.11
- Required packages listed in `requirements.txt`

### Installation
1. Clone the repository:
    ```
    git clone https://github.com/teohj01/HDB-Resale-Price-Prediction.git
    cd HDB-Resale-Price-Prediction
    ```

2. Create and activate a conda environment:
    ```
    conda create -n hdbenv python=3.11
    conda activate hdbenv
    ```

3. Install the required packages:
    ```
    pip install -r requirements.txt
    ```

## Pipeline Execution
To run the complete pipeline, execute:
```
python main.py
```

This will:
1. Load and clean the data
2. Preprocess features
3. Split data into training, validation, and test sets
4. Train baseline models
5. Perform hyperparameter tuning
6. Evaluate models and select the best performing model

## Logical Flow of the Pipeline

### 1. Configuration (`config.yaml`)
The pipeline starts with loading configuration parameters from `src/config.yaml`, which includes:
- Data file path
- Target column name
- Feature categorization (numerical, nominal, ordinal)
- Train/validation/test split ratios
- Hyperparameter grid for model tuning

### 2. Data Preparation (`DataPreparation` class)
The `DataPreparation` class handles:
- Removing duplicates
- Standardizing flat type names
- Converting storey ranges to numerical values
- Filling missing town and flat model names
- Extracting year and month from date
- Converting remaining lease information to months
- Concatenating block and street name to create a full address
- Calculating the nearest distance from each address to various amenities (school, MRT/LRT station, mall)
- Creating a preprocessor for feature transformation

### 3. Model Training (`ModelTraining` class)
The `ModelTraining` class manages:
- Splitting data into training, validation and test sets
- Training baseline methods (Linear Regression, Ridge, Lasso)
- Hyperparameter tuning for Ridge and Lasso models 
Evaluating models using multiple metrics (MAE, MSE, RMSE, R²)
- Selecting the best model based on R² score

### 4. Main Execution (`main.py`)
The main script orchestrates the entire pipeline by:
- Loading configuration and data
- Initializing data preparation and model training
- Running the training and evaluation process
- Identifying and evaluating the best model on the test set

## Key Findings and Feature Handling

### Exploratory Data Analysis

Before diving into the model training process, an exploratory data analysis (EDA) was conducted to understand the data better and identify any potential issues. Here are some key findings from the EDA:

**EDA Findings and Explanations**:

#### Dataset Overview
- The dataset contains 88,688 resale transactions across 14 columns, covering flat characteristics, lease details, location, and resale price.
- 4,223 duplicate rows were identified and removed, reducing the dataset to 84,465 transactions.

#### Univariate Analysis
- '4 ROOM' flats are the most common flat type, followed by '3 ROOM' and '5 ROOM'. '1 ROOM' and 'MULTI-GENERATION' flats are rare.
- Resale price is right-skewed, ranging from $160,000 to $1.2 million, with a mean of $438,810 exceeding the median of $408,000, indicating a small number of high-value transactions pull the average upward.
- July 2018 recorded the highest number of listings in the dataset. There's a recurring seasonal dip around February most years, possibly linked to Chinese New Year and BTO launch timing.

#### Bivariate Analysis
- Median resale price increases with flat size; 'EXECUTIVE' and 'MULTI-GENERATION' flats have the highest medians, while '1 ROOM' and '2 ROOM' have the lowest and most consistent pricing.
- Floor area and resale price are positively related, larger flats generally sell for more, though considerable price variation exists even among similarly-sized flats, suggesting other factors also drive price.
- 9 records with floor areas of 174-280 sqm and prices of $810,000-$1.185 million were flagged as '3 ROOM' outliers. Investigation confirmed these are legitimate HDB Terrace houses, a rare landed flat type built in the 1950s in Kallang/Whampoa, and were retained rather than removed.

#### Correlation Analysis
- Spearman rank correlation was used instead of Pearson because it is more robust to the outliers and skewed distributions identified above, and captures monotonic relationships.
- `floor_area_sqm` shows a strong positive correlation with `resale_price`.
- `lease_commence_date` shows a moderate positive correlation with `resale_price`.
- `storey_range` shows a weak positive correlation with `resale_price`.

### Data Cleaning
- Storey ranges are converted to their average values because the original values were strings like '07 TO 09', and taking the midpoint converts them into a single numerical value usable in both correlation analysis and machine learning models, which require numeric input.
- Remaining lease information is extracted and converted to total months because the original `remaining_lease` column was stored as text in inconsistent formats (e.g. '70 years 03 months', '81', '66 years'), and converting all entries into a single standardized unit (months) makes it usable as a numerical feature.
- Year and month are extracted from the transaction date because the original `month` column combined year and month into a single string (e.g. '2018-05'), which isn't suitable for machine learning models that require numerical input.
- Missing town and flat model names are filled using ID-to-name mappings because `town_id` and `flatm_id` map consistently to their respective `town_name` and `flatm_name` values elsewhere in the dataset, so the missing names can be reliably recovered by mapping each ID to its corresponding name from other rows, rather than dropping the rows or imputing arbitrarily.
- Full address were engineered because combining `block` and `street_name` created a geocodable address that could be passed to Singapore's OneMap API to obtain coordinates, which were then used to calculate each flat's distance to the nearest school, MRT station, and shopping mall, amenities that domain knowledge suggests significantly affect resale price.

### Feature Processing
- **Numerical Features**: `floor_area_sqm`, `remaining_lease_months`, `lease_commence_date`, `year`, `distance_to_school`, `distance_to_mrt`, `distance_to_mall`
- Standardized using `StandardScaler` because the numerical features are approximately normally distributed but vary significantly in scale, and standardisation suits the scale-sensitive algorithms (linear models) planned for this analysis.
- **Nominal Features**: `month`, `town_name`, `flatm_name` - Encoded using `OneHotEncoder` because these are unordered categories, there is no inherent ranking among different months, towns, or flat models, so one-hot encoding avoids implying a false ordinal relationship.
- **Ordinal Features**: `flat_type` - Encoded using `OrdinalEncoder` with predefined categories because `flat_type` has a natural, meaningful order based on size, and ordinal encoding preserves this ordering as a single numeric feature rather than creating unnecessary dummy variables.
- **Passthrough Features**: `storey_range` - Used as-is after converting to numerical values because it was already converted into a numerical value (the average of the range) during the correlation analysis stage, so no additional encoding was needed.

## Model Choices and Evaluation

### Models Implemented and Justifications
1. **Linear Regression**: Basic model without regularization because it serves as a simple, interpretable baseline against which the performance of the regularized models (Ridge, Lasso) can be measured.
2. **Ridge Regression**: Linear regression with L2 regularization because it shrinks coefficient magnitudes to reduce overfitting and stabilize estimates without eliminating any features entirely.
3. **Lasso Regression**: Linear regression with L1 regularization because it can shrink some coefficients exactly to zero, effectively performing feature selection, useful given the large number of one-hot encoded columns produced from `town_name` and `flatm_name`.

### Hyperparameter Tuning
- Grid search is performed for Ridge and Lasso models because default hyperparameters (e.g. alpha=1) are rarely optimal, and grid search systematically evaluates multiple alpha and fit_intercept combinations to find the one that maximizes validation performance, rather than relying on an arbitrary default.
- Parameters tuned include `alpha` and `fit_intercept` because `alpha` controls the strength of regularization, directly affecting the bias-variance tradeoff, while `fit_intercept` determines whether the model fits an intercept term, relevant here since the numerical features are standardized around a mean of zero.
- 5-fold cross-validation is used during tuning because it evaluates each hyperparameter combination across 5 different train/validation splits of the training data, reducing the risk of selecting a hyperparameter that only performs well on one specific split by chance.

### Evaluation Metrics
- **MAE (Mean Absolute Error)**: Average absolute difference between predicted and actual prices
- **MSE (Mean Squared Error)**: Average squared difference between predicted and actual prices
- **RMSE (Root Mean Squared Error)**: Square root of MSE, in the same unit as the target
- **R² (Coefficient of Determination)**: Proportion of variance explained by the model
