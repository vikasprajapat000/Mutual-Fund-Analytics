"""
Mutual Fund Analytics - Day 1 Ingestion Profiler
This script scans and profiles raw mutual fund datasets by printing shape,
data types, columns, head records, and missing values.

Usage:
    python data_ingestion.py
"""

import os
import pandas as pd


def profile_raw_files() -> None:
    """Scan and output profiles for all 10 raw mutual fund CSV files."""
    raw_dir = os.path.join("data", "raw")

    datasets = {
        "Fund Master": "01_fund_master.csv",
        "NAV History": "02_nav_history.csv",
        "AUM by Fund House": "03_aum_by_fund_house.csv",
        "Monthly SIP Inflows": "04_monthly_sip_inflows.csv",
        "Category Inflows": "05_category_inflows.csv",
        "Industry Folio Count": "06_industry_folio_count.csv",
        "Scheme Performance": "07_scheme_performance.csv",
        "Investor Transactions": "08_investor_transactions.csv",
        "Portfolio Holdings": "09_portfolio_holdings.csv",
        "Benchmark Indices": "10_benchmark_indices.csv",
    }

    print("=" * 60)
    print("      MUTUAL FUND ANALYTICS - RAW DATA PROFILE SCAN")
    print("=" * 60)

    for name, filename in datasets.items():
        filepath = os.path.join(raw_dir, filename)
        print("-" * 60)
        print(f"Dataset: {name} ({filename})")
        print("-" * 60)

        if not os.path.exists(filepath):
            print(f"WARNING: File not found at {filepath}")
            continue

        try:
            df = pd.read_csv(filepath)
            print(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns")
            print(f"Columns: {df.columns.tolist()}")
            print("\nData Types:")
            print(df.dtypes)
            print("\nMissing Values:")
            print(df.isnull().sum())
            print("\nFirst 3 Records:")
            print(df.head(3).to_string())
        except pd.errors.EmptyDataError:
            print("ERROR: File is empty.")
        except Exception as err:
            print(f"ERROR: Failed to read file: {err}")
        print("\n")


if __name__ == "__main__":
    profile_raw_files()