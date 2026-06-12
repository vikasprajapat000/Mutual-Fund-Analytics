"""
Mutual Fund Analytics - Day 1 Live NAV Fetcher
Fetches historical NAV timeseries from the Association of Mutual Funds in India (AMFI)
open API endpoint (api.mfapi.in) for active verification tracking.

Usage:
    python live_nav_fetch.py
"""

import os
import requests
import pandas as pd


def fetch_live_nav_data() -> None:
    """Fetch live NAV data from mfapi.in API and write them to raw CSV files."""
    raw_dir = os.path.join("data", "raw")
    os.makedirs(raw_dir, exist_ok=True)

    print("============================================================")
    print("      MUTUAL FUND ANALYTICS - LIVE NAV API FETCH")
    print("============================================================")

    # 1. Fetch reference HDFC Top 100 Scheme (AMFI Code: 125497)
    url_hdfc = "https://api.mfapi.in/mf/125497"
    try:
        response = requests.get(url_hdfc, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        nav_records = data.get("data", [])
        if nav_records:
            nav_df = pd.DataFrame(nav_records)
            save_path = os.path.join(raw_dir, "hdfc_top100_live_nav.csv")
            nav_df.to_csv(save_path, index=False)
            
            scheme_name = data.get("meta", {}).get("scheme_name", "Unknown Scheme")
            print(f"SUCCESS: Fetched {scheme_name}")
            print(f"Saved: {save_path} ({len(nav_df)} rows)")
            print(nav_df.head(3).to_string())
        else:
            print("WARNING: No NAV data found in API response for HDFC Top 100.")
    except Exception as err:
        print(f"ERROR: Failed to fetch HDFC Top 100 live NAV: {err}")

    print("-" * 60)

    # 2. Fetch other selected large cap mutual funds
    funds = {
        "SBI_Bluechip": 119551,
        "ICICI_Bluechip": 120503,
        "Nippon_Large_Cap": 118632,
        "Axis_Bluechip": 119092,
        "Kotak_Bluechip": 120841,
    }

    for name, code in funds.items():
        url = f"https://api.mfapi.in/mf/{code}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            nav_records = data.get("data", [])
            if nav_records:
                nav_df = pd.DataFrame(nav_records)
                save_path = os.path.join(raw_dir, f"{name}.csv")
                nav_df.to_csv(save_path, index=False)
                print(f"SUCCESS: Saved {name}.csv ({len(nav_df)} rows)")
            else:
                print(f"WARNING: No NAV data found in API response for {name} ({code}).")
        except Exception as err:
            print(f"ERROR: Failed to fetch {name} ({code}): {err}")

    print("\nLive NAV fetch execution complete.\n")


if __name__ == "__main__":
    fetch_live_nav_data()