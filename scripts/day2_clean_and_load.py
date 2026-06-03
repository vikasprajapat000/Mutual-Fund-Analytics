import pandas as pd
import numpy as np
import os
import sqlite3
from sqlalchemy import create_engine, text

# File paths
DATA_DIR = 'data'
RAW_DIR = os.path.join(DATA_DIR, 'raw')
PROC_DIR = os.path.join(DATA_DIR, 'processed')
DB_DIR = os.path.join(DATA_DIR, 'db')
DB_PATH = os.path.join(DB_DIR, 'bluestock_mf.db')
SCHEMA_PATH = 'sql/schema.sql'

# Create directories if they don't exist
os.makedirs(PROC_DIR, exist_ok=True)
os.makedirs(DB_DIR, exist_ok=True)

print("Starting Day 2 Data Cleaning...")

# ==========================================
# 1. Clean nav_history.csv
# ==========================================
print("\nCleaning 02_nav_history.csv...")
nav_df = pd.read_csv(os.path.join(RAW_DIR, '02_nav_history.csv'))
print(f"Original rows: {len(nav_df)}")

# Parse dates
nav_df['date'] = pd.to_datetime(nav_df['date'])

# Sort by amfi_code + date
nav_df = nav_df.sort_values(by=['amfi_code', 'date'])

# Remove duplicates
nav_df = nav_df.drop_duplicates(subset=['amfi_code', 'date'], keep='last')

# Validate NAV > 0 (drop invalid rows)
nav_df = nav_df[nav_df['nav'] > 0]

# Forward-fill missing NAV for holidays/weekends
# Create a complete date range per fund
def fill_missing_dates(group):
    if len(group) == 0:
        return group
    idx = pd.date_range(group['date'].min(), group['date'].max())
    group = group.set_index('date').reindex(idx)
    group['amfi_code'] = group['amfi_code'].ffill()
    group['nav'] = group['nav'].ffill()
    return group.reset_index().rename(columns={'index': 'date'})

nav_df = nav_df.groupby('amfi_code').apply(fill_missing_dates).reset_index(drop=True)
print(f"Cleaned rows after ffill: {len(nav_df)}")
nav_df.to_csv(os.path.join(PROC_DIR, '02_nav_history_cleaned.csv'), index=False)


# ==========================================
# 2. Clean investor_transactions.csv
# ==========================================
print("\nCleaning 08_investor_transactions.csv...")
txn_df = pd.read_csv(os.path.join(RAW_DIR, '08_investor_transactions.csv'))
print(f"Original rows: {len(txn_df)}")

# Standardise transaction_type
type_map = {
    'sip': 'SIP', 'Sip': 'SIP', 'systematic investment plan': 'SIP',
    'lumpsum': 'Lumpsum', 'LUMP': 'Lumpsum', 'One Time': 'Lumpsum',
    'redemption': 'Redemption', 'Redeem': 'Redemption', 'Withdraw': 'Redemption'
}
txn_df['transaction_type'] = txn_df['transaction_type'].replace(type_map)

# Validate amount > 0
txn_df = txn_df[txn_df['amount_inr'] > 0]

# Fix date formats
txn_df['transaction_date'] = pd.to_datetime(txn_df['transaction_date']).dt.date

# Check KYC status enum values
valid_kyc = ['Verified', 'Pending', 'Rejected']
txn_df = txn_df[txn_df['kyc_status'].isin(valid_kyc)]

print(f"Cleaned rows: {len(txn_df)}")
txn_df.to_csv(os.path.join(PROC_DIR, '08_investor_transactions_cleaned.csv'), index=False)


# ==========================================
# 3. Clean scheme_performance.csv
# ==========================================
print("\nCleaning 07_scheme_performance.csv...")
perf_df = pd.read_csv(os.path.join(RAW_DIR, '07_scheme_performance.csv'))
print(f"Original rows: {len(perf_df)}")

# Validate numeric return columns
return_cols = ['return_1yr_pct', 'return_3yr_pct', 'return_5yr_pct']
for col in return_cols:
    perf_df[col] = pd.to_numeric(perf_df[col], errors='coerce')

# Flag anomalies (e.g. returns > 1000% or < -100%)
perf_df['is_anomaly'] = False
for col in return_cols:
    perf_df.loc[(perf_df[col] > 1000) | (perf_df[col] < -100), 'is_anomaly'] = True

# Check expense_ratio range (0.1% – 2.5%)
perf_df.loc[(perf_df['expense_ratio_pct'] < 0.1) | (perf_df['expense_ratio_pct'] > 2.5), 'expense_ratio_pct'] = np.nan

print(f"Cleaned rows: {len(perf_df)}")
perf_df.to_csv(os.path.join(PROC_DIR, '07_scheme_performance_cleaned.csv'), index=False)


# ==========================================
# 4. Process remaining datasets (simple copy for this day's scope)
# ==========================================
print("\nProcessing remaining datasets...")
other_files = [
    '01_fund_master.csv', '03_aum_by_fund_house.csv', '04_monthly_sip_inflows.csv',
    '05_category_inflows.csv', '06_industry_folio_count.csv', '09_portfolio_holdings.csv',
    '10_benchmark_indices.csv'
]
dfs = {}
dfs['dim_fund'] = pd.read_csv(os.path.join(RAW_DIR, '01_fund_master.csv'))
dfs['fact_aum'] = pd.read_csv(os.path.join(RAW_DIR, '03_aum_by_fund_house.csv'))

for file in other_files:
    df = pd.read_csv(os.path.join(RAW_DIR, file))
    df.to_csv(os.path.join(PROC_DIR, file.replace('.csv', '_cleaned.csv')), index=False)
print("Saved 10 cleaned CSVs in data/processed/")

# ==========================================
# 5. Generate dim_date from nav_history
# ==========================================
all_dates = pd.date_range(start=nav_df['date'].min(), end=nav_df['date'].max())
dim_date = pd.DataFrame({'date': all_dates})
dim_date['year'] = dim_date['date'].dt.year
dim_date['month'] = dim_date['date'].dt.month
dim_date['day'] = dim_date['date'].dt.day
dim_date['quarter'] = dim_date['date'].dt.quarter
dim_date['day_of_week'] = dim_date['date'].dt.dayofweek
dim_date['is_weekend'] = dim_date['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)
dim_date['date'] = dim_date['date'].dt.date
nav_df['date'] = nav_df['date'].dt.date # Convert back to date for sqlite

# ==========================================
# 6. Load datasets into SQLite
# ==========================================
print("\nLoading data into SQLite...")
engine = create_engine(f'sqlite:///{DB_PATH}')

# Execute schema.sql to create tables
with open(SCHEMA_PATH, 'r') as f:
    schema_sql = f.read()

with engine.connect() as conn:
    for statement in schema_sql.split(';'):
        if statement.strip():
            conn.execute(text(statement))

# Load data into tables
print("Loading dim_fund...")
dfs['dim_fund'].to_sql('dim_fund', engine, if_exists='append', index=False)

print("Loading dim_date...")
dim_date.to_sql('dim_date', engine, if_exists='append', index=False)

print("Loading fact_nav...")
nav_df[['amfi_code', 'date', 'nav']].to_sql('fact_nav', engine, if_exists='append', index=False)

print("Loading fact_transactions...")
txn_df.to_sql('fact_transactions', engine, if_exists='append', index=False)

print("Loading fact_performance...")
exclude_cols = ['is_anomaly', 'scheme_name', 'fund_house', 'category', 'plan']
perf_cols = [c for c in perf_df.columns if c not in exclude_cols]
perf_df[perf_cols].to_sql('fact_performance', engine, if_exists='append', index=False)

print("Loading fact_aum...")
dfs['fact_aum'].to_sql('fact_aum', engine, if_exists='append', index=False)

print("\nData loading complete! Verifying row counts...")

# Verify row counts
tables = ['dim_fund', 'dim_date', 'fact_nav', 'fact_transactions', 'fact_performance', 'fact_aum']
with engine.connect() as conn:
    for table in tables:
        count = pd.read_sql(f'SELECT COUNT(*) as cnt FROM {table}', conn).iloc[0]['cnt']
        print(f"Table {table}: {count} rows")

print("\nDay 2 Tasks Finished Successfully!")
