import os

import pandas as pd
import requests
from dotenv import load_dotenv

stations = [
    # North-South Line
    "Jurong East (NS1)",
    "Bukit Batok (NS2)",
    "Bukit Gombak (NS3)",
    "Choa Chu Kang (NS4)",
    "Yew Tee (NS5)",
    "Kranji (NS7)",
    "Marsiling (NS8)",
    "Woodlands (NS9)",
    "Admiralty (NS10)",
    "Sembawang (NS11)",
    "Canberra (NS12)",
    "Yishun (NS13)",
    "Khatib (NS14)",
    "Yio Chu Kang (NS15)",
    "Ang Mo Kio (NS16)",
    "Bishan (NS17)",
    "Braddell (NS18)",
    "Toa Payoh (NS19)",
    "Novena (NS20)",
    "Newton (NS21)",
    "Orchard (NS22)",
    "Somerset (NS23)",
    "Dhoby Ghaut (NS24)",
    "City Hall (NS25)",
    "Raffles Place (NS26)",
    "Marina Bay (NS27)",
    "Marina South Pier (NS28)",

    # East-West Line
    "Pasir Ris (EW1)",
    "Tampines (EW2)",
    "Simei (EW3)",
    "Tanah Merah (EW4)",
    "Bedok (EW5)",
    "Kembangan (EW6)",
    "Eunos (EW7)",
    "Paya Lebar (EW8)",
    "Aljunied (EW9)",
    "Kallang (EW10)",
    "Lavender (EW11)",
    "Bugis (EW12)",
    "Tanjong Pagar (EW15)",
    "Outram Park (EW16)",
    "Tiong Bahru (EW17)",
    "Redhill (EW18)",
    "Queenstown (EW19)",
    "Commonwealth (EW20)",
    "Buona Vista (EW21)",
    "Dover (EW22)",
    "Clementi (EW23)",
    "Chinese Garden (EW25)",
    "Lakeside (EW26)",
    "Boon Lay (EW27)",
    "Pioneer (EW28)",
    "Joo Koon (EW29)",
    "Gul Circle (EW30)",
    "Tuas Crescent (EW31)",
    "Tuas West Road (EW32)",
    "Tuas Link (EW33)",
    "Expo (CG1)",
    "Changi Airport (CG2)",

    # North East Line
    "HarbourFront (NE1)",
    "Chinatown (NE3)",
    "Clarke Quay (NE4)",
    "Little India (NE6)",
    "Farrer Park (NE7)",
    "Boon Keng (NE8)",
    "Potong Pasir (NE9)",
    "Woodleigh (NE10)",
    "Serangoon (NE11)",
    "Kovan (NE12)",
    "Hougang (NE13)",
    "Buangkok (NE14)",
    "Sengkang (NE15)",
    "Punggol (NE16)",
    "Punggol Coast (NE17)",

    # Circle Line
    "Bras Basah (CC2)",
    "Esplanade (CC3)",
    "Promenade (CC4)",
    "Nicoll Highway (CC5)",
    "Stadium (CC6)",
    "Mountbatten (CC7)",
    "Dakota (CC8)",
    "MacPherson (CC10)",
    "Tai Seng (CC11)",
    "Bartley (CC12)",
    "Lorong Chuan (CC14)",
    "Marymount (CC16)",
    "Caldecott (CC17)",
    "Botanic Gardens (CC18)",
    "Farrer Road (CC19)",
    "Holland Village (CC20)",
    "one-north (CC22)",
    "Kent Ridge (CC23)",
    "Haw Par Villa (CC24)",
    "Pasir Panjang (CC25)",
    "Labrador Park (CC26)",
    "Telok Blangah (CC27)",
    "Keppel (CC29)",
    "Cantonment (CC30)",
    "Prince Edward Road (CC31)",
    "Bayfront (CC33)",

    # Downtown Line
    "Bukit Panjang (DT1)",
    "Cashew (DT2)",
    "Hillview (DT3)",
    "Hume (DT4)",
    "Beauty World (DT5)",
    "King Albert Park (DT6)",
    "Sixth Avenue (DT7)",
    "Stevens (DT9)",
    "Rochor (DT12)",
    "Downtown (DT16)",
    "Telok Ayer (DT17)",
    "Fort Canning (DT19)",
    "Bencoolen (DT20)",
    "Jalan Besar (DT21)",
    "Geylang Bahru (DT22)",
    "Mattar (DT23)",
    "Ubi (DT25)",
    "Kaki Bukit (DT26)",
    "Bedok North (DT27)",
    "Bedok Reservoir (DT28)",
    "Tampines West (DT29)",
    "Tampines East (DT31)",
    "Upper Changi (DT32)",
    "Xilin (DT34)",
    "Sungei Bedok (DT35)",

    # Thomson-East Coast Line
    "Woodlands North (TE1)",
    "Woodlands South (TE3)",
    "Springleaf (TE4)",
    "Lentor (TE5)",
    "Mayflower (TE6)",
    "Bright Hill (TE7)",
    "Upper Thomson (TE8)",
    "Mount Pleasant (TE10)",
    "Napier (TE11)",
    "Orchard Boulevard (TE12)",
    "Great World (TE14)",
    "Havelock (TE15)",
    "Maxwell (TE17)",
    "Shenton Way (TE18)",
    "Gardens by the Bay (TE20)",
    "Tanjong Rhu (TE21)",
    "Katong Park (TE22)",
    "Tanjong Katong (TE23)",
    "Marine Parade (TE24)",
    "Marine Terrace (TE25)",
    "Siglap (TE26)",
    "Bayshore (TE27)",

    # Bukit Panjang LRT
    "South View (BP2)",
    "Keat Hong (BP3)",
    "Teck Whye (BP4)",
    "Phoenix (BP5)",
    "Bukit Panjang (BP6)",
    "Petir (BP7)",
    "Pending (BP8)",
    "Bangkit (BP9)",
    "Fajar (BP10)",
    "Segar (BP11)",
    "Jelapang (BP12)",
    "Senja (BP13)",

    # Sengkang LRT - East Loop (SE1-SE5)
    "Compassvale (SE1)",
    "Rumbia (SE2)",
    "Bakau (SE3)",
    "Kangkar (SE4)",
    "Ranggung (SE5)",

    # Sengkang LRT - West Loop (SW1-SW8)
    "Cheng Lim (SW1)",
    "Farmway (SW2)",
    "Kupang (SW3)",
    "Thanggam (SW4)",
    "Fernvale (SW5)",
    "Layar (SW6)",
    "Tongkang (SW7)",
    "Renjong (SW8)",

    # Punggol LRT - East Loop (PE1-PE7)
    "Cove (PE1)",
    "Meridian (PE2)",
    "Coral Edge (PE3)",
    "Riviera (PE4)",
    "Kadaloor (PE5)",
    "Oasis (PE6)",
    "Damai (PE7)",

    # Punggol LRT - West Loop (PW1-PW7)
    "Sam Kee (PW1)",
    "Teck Lee (PW2)",
    "Punggol Point (PW3)",
    "Samudera (PW4)",
    "Nibong (PW5)",
    "Sumang (PW6)",
    "Soo Teck (PW7)",
]

# Line codes starting with these prefixes are LRT lines; everything else is MRT.
LRT_PREFIXES = ("BP", "SE", "SW", "PE", "PW")

def get_onemap_token(email: str, password: str) -> str:
    resp = requests.post(
        "https://www.onemap.gov.sg/api/auth/post/getToken",
        json={"email": email, "password": password},
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def geocode(station: str, headers: dict) -> tuple:
    resp = requests.get(
        "https://www.onemap.gov.sg/api/common/elastic/search",
        params={"searchVal": station, "returnGeom": "Y", "getAddrDetails": "N", "pageNum": 1},
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
    for name in stations:
        station_name, code = name.rsplit(" (", 1)
        code = code.rstrip(")")
        line_type = "LRT" if code.startswith(LRT_PREFIXES) else "MRT"

        lat, lon = geocode(f"{station_name} {line_type} STATION", headers)
        if lat is None:
            print(f"Not found: {name}")
        new_rows.append({"station_name": name, "latitude": lat, "longitude": lon})

    station_df = pd.DataFrame(new_rows)

    os.makedirs("data", exist_ok=True)
    station_df.to_csv("data/station_coords.csv", index=False)
    missing = station_df["latitude"].isna().sum()
    print(f"Saved {len(station_df)} stations to data/station_coords.csv. {missing} missing coordinates for station(s) were found.")


if __name__ == "__main__":
    main()
