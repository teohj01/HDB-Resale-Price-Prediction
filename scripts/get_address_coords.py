import os

import pandas as pd
import requests
from dotenv import load_dotenv

INPUT_PATH = "data/resale_transactions_v2.csv"
OUTPUT_PATH = "data/cleaned_resale_transactions.csv"


def get_onemap_token(email: str, password: str) -> str:
    resp = requests.post(
        "https://www.onemap.gov.sg/api/auth/post/getToken",
        json={"email": email, "password": password},
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def geocode_address(address: str, headers: dict) -> tuple:
    resp = requests.get(
        "https://www.onemap.gov.sg/api/common/elastic/search",
        params={"searchVal": address, "returnGeom": "Y", "getAddrDetails": "N", "pageNum": 1},
        headers=headers,
    )
    resp.raise_for_status()
    results = resp.json().get("results", [])
    if not results:
        return (None, None)
    return (float(results[0]["LATITUDE"]), float(results[0]["LONGITUDE"]))


def main():
    load_dotenv()
    token = get_onemap_token(os.getenv("ONEMAP_EMAIL"), os.getenv("ONEMAP_PASSWORD"))
    headers = {"Authorization": token}

    df = pd.read_csv(INPUT_PATH)
    unique_addresses = df["full_address"].unique()

    new_rows = []
    for address in unique_addresses:
        lat, lon = geocode_address(address, headers)
        if lat is None:
            print(f"Not found: {address}")
        new_rows.append({"full_address": address, "latitude": lat, "longitude": lon})

    geocode_cache = pd.DataFrame(new_rows)

    df = df.merge(geocode_cache, on="full_address", how="left")

    os.makedirs("data", exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    missing = df["latitude"].isna().sum()
    print(f"Saved {len(df)} rows to {OUTPUT_PATH}. {missing} missing coordinates for address(es) were found.")


if __name__ == "__main__":
    main()
