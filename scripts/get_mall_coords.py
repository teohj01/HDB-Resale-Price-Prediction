import os

import pandas as pd
import requests
from dotenv import load_dotenv

shopping_malls = [
    '100 AM',
    '313@Somerset',
    '321 Clementi',
    '600 @ Toa Payoh',
    '888 Plaza',
    'AMK Hub',
    'Admiralty Place',
    'Alexandra Retail Centre',
    'Anchorpoint',
    'Beauty World Centre',
    'Beauty World Plaza',
    'Bedok Mall',
    'Bukit Panjang Plaza',
    'Bukit Timah Plaza',
    'Buangkok Square',
    'Bugis+',
    'Bugis Junction',
    'Canberra Plaza',
    'Capitol Singapore',
    'Cathay Cineleisure Orchard',
    'Causeway Point',
    'Century Square',
    'Changi City Point',
    'Chinatown Point',
    'City Square Mall',
    'CityLink Mall',
    'CQ @ Clarke Quay',
    'Claymore Connect',
    'Clementi Mall',
    'Compass One',
    'Concorde Shopping Mall',
    'Dawson Place',
    'Delfi Orchard',
    'Depot Heights Shopping Centre',
    'Djitsun Mall',
    'Eastpoint Mall',
    'Elias Mall',
    'Esplanade Mall',
    'Fajar Shopping Centre',
    'Far East Plaza',
    'Forum The Shopping Mall',
    'Funan',
    'GV Yishun',
    'Gek Poh Shopping Centre',
    'Great World',
    'Greenridge Shopping Centre',
    'HDB Hub',
    'Heartland Mall',
    'Hillion Mall',
    'Holland Piazza',
    'Holland Road Shopping Centre',
    'Holland Village',
    'Hougang 1',
    'Hougang Mall',
    'IMM',
    'ION Orchard',
    'Jem',
    'Jewel Changi Airport',
    'Junction 10',
    'Junction 8',
    'Junction Nine',
    'Jurong Point',
    'KINEX',
    'Kallang Wave Mall',
    'Katong Shopping Centre',
    'Leisure Park Kallang',
    'Limbang Shopping Centre',
    'Lot One',
    'Loyang Point',
    'Lucky Plaza',
    'Mandarin Gallery',
    'Marina Bay Link Mall',
    'Marina Square',
    'Millenia Walk',
    'Mustafa Centre',
    'Ngee Ann City',
    'Nex',
    'Northpoint City',
    'Northshore Plaza',
    'Novena Square',
    'Oasis Terraces',
    'Orchard Central',
    'Orchard Gateway',
    'Orchard Plaza',
    'Our Tampines Hub',
    'PLQ Mall',
    'Palais Renaissance',
    'Parkway Parade',
    'Pasir Ris West Plaza',
    'Paya Lebar Square',
    'Peninsula Plaza',
    'Pioneer Mall',
    'Plaza Singapura',
    'Punggol Plaza',
    'Queensway Shopping Centre',
    'Raffles City',
    'Rivervale Mall',
    'Rochester Mall',
    'Sembawang Shopping Centre',
    'Sengkang Grand Mall',
    'Shaw House',
    'Shaw Centre',
    'Sim Lim Square',
    'SingPost Centre',
    'Sun Plaza',
    'Suntec City Mall',
    'Sunshine Place',
    'Taman Jurong Shopping Centre',
    'Tang Plaza',
    'Tanglin Mall',
    'Tampines 1',
    'Tampines Mall',
    'Tekka Place',
    'The Cathay',
    'The Centrepoint',
    'The Paragon',
    'The Rail Mall',
    'The Seletar Mall',
    'The Shoppes at Marina Bay Sands',
    'The Star Vista',
    'The Woodleigh Mall',
    'Thomson Plaza',
    'Tiong Bahru Plaza',
    'United Square',
    'Upper Serangoon Shopping Centre',
    'Valley Point',
    'Vista Point',
    'VivoCity',
    'Waterway Point',
    'West Coast Plaza',
    'West Mall',
    'Westgate',
    'White Sands',
    'Wheelock Place',
    'Wisma Atria',
    'Wisma Geylang Serai',
    'Wisteria Mall',
    'Woodlands North Plaza',
    'Yew Tee Point',
    'Yew Tee Square',
    'myVillage @ Serangoon',
]


def get_onemap_token(email: str, password: str) -> str:
    resp = requests.post(
        "https://www.onemap.gov.sg/api/auth/post/getToken",
        json={"email": email, "password": password},
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def geocode(mall: str, headers: dict) -> tuple:
    resp = requests.get(
        "https://www.onemap.gov.sg/api/common/elastic/search",
        params={"searchVal": mall, "returnGeom": "Y", "getAddrDetails": "N", "pageNum": 1},
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

    new_rows = []
    for name in shopping_malls:
        lat, lon = geocode(name, headers)
        if lat is None:
            print(f"Not found: {name}")
        new_rows.append({"mall_name": name, "latitude": lat, "longitude": lon})

    mall_df = pd.DataFrame(new_rows)

    os.makedirs("data", exist_ok=True)
    mall_df.to_csv("data/mall_coords.csv", index=False)
    missing = mall_df["latitude"].isna().sum()
    print(f"Saved {len(mall_df)} malls to data/mall_coords.csv. {missing} missing coordinates for mall(s) were found.")


if __name__ == "__main__":
    main()
