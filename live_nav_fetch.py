import requests
import pandas as pd

url = "https://api.mfapi.in/mf/125497"
try:
    response = requests.get(url)
    data = response.json()
    nav_df = pd.DataFrame(data["data"])
    nav_df.to_csv("data/raw/hdfc_top100_live_nav.csv", index=False)
    print(nav_df.head())
except Exception as e:
    print(f"Error fetching hdfc: {e}")

funds = {
    "SBI_Bluechip": 119551,
    "ICICI_Bluechip": 120503,
    "Nippon_Large_Cap": 118632,
    "Axis_Bluechip": 119092,
    "Kotak_Bluechip": 120841
}

for name, code in funds.items():
    try:
        url = f"https://api.mfapi.in/mf/{code}"
        response = requests.get(url)
        data = response.json()
        nav_df = pd.DataFrame(data["data"])
        nav_df.to_csv(f"data/raw/{name}.csv", index=False)
        print(f"{name} saved")
    except Exception as e:
        print(f"Error for {name}: {e}")