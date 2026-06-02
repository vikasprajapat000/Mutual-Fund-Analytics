import pandas as pd

# STEP 9: Explore Fund Master
try:
    df = pd.read_csv("data/raw/01_fund_master.csv")
    print("Unique Fund Houses")
    print(df['fund_house'].unique())
    print("Categories")
    print(df['category'].unique())
    print("Sub Categories")
    print(df['sub_category'].unique())
    print("Risk Grades")
    print(df['risk_grade'].unique())

    # STEP 10: Understand AMFI Scheme Code
    print(df[['scheme_code']].head())

    # STEP 11: Validate AMFI Codes
    nav_history = pd.read_csv("data/raw/02_nav_history.csv")
    master_codes = set(df['scheme_code'])
    nav_codes = set(nav_history['scheme_code'])
    missing_codes = master_codes - nav_codes
    print("Missing Codes:")
    print(len(missing_codes))
except Exception as e:
    print(f"Error: {e}")
