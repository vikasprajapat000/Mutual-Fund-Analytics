import pandas as pd

files = {
    "Fund Master": "data/raw/01_fund_master.csv",
    "NAV History": "data/raw/02_nav_history.csv",
    "AUM": "data/raw/03_aum_by_fund_house.csv",
    "SIP": "data/raw/04_monthly_sip_inflows.csv",
    "Category Inflows": "data/raw/05_category_inflows.csv",
    "Industry Folio": "data/raw/06_industry_folio_count.csv",
    "Performance": "data/raw/07_scheme_performance.csv",
    "Transactions": "data/raw/08_investor_transactions.csv",
    "Portfolio": "data/raw/09_portfolio_holdings.csv",
    "Benchmark": "data/raw/10_benchmark_indices.csv"
}

for name, path in files.items():

    print("\n" + "="*80)
    print(name)
    print("="*80)

    try:
        df = pd.read_csv(path)

        print("\nShape:")
        print(df.shape)

        print("\nColumns:")
        print(df.columns.tolist())

        print("\nDtypes:")
        print(df.dtypes)

        print("\nHead:")
        print(df.head())

        print("\nMissing Values:")
        print(df.isnull().sum())

    except Exception as e:
        print(f"Error: {e}")