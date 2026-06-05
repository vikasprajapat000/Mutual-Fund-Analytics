import pandas as pd
import numpy as np
import os
from sqlalchemy import create_engine, text

RAW  = os.path.join('data', 'raw')
PROC = os.path.join('data', 'processed')
DB   = os.path.join('data', 'db', 'bluestock_mf.db')

os.makedirs(PROC, exist_ok=True)
os.makedirs(os.path.join('data', 'db'), exist_ok=True)

print('Day 2 — Data Cleaning + SQLite Load')
print('=' * 50)


# 1. Clean nav_history
print('\n[1/7] Cleaning NAV history...')
nav = pd.read_csv(os.path.join(RAW, '02_nav_history.csv'))
print('  Before:', nav.shape)
nav['date'] = pd.to_datetime(nav['date'])
nav = nav.sort_values(['amfi_code', 'date'])
nav = nav.drop_duplicates(subset=['amfi_code', 'date'], keep='last')
nav = nav[nav['nav'] > 0]

filled_list = []
for code, group in nav.groupby('amfi_code'):
    group = group.sort_values('date')
    idx   = pd.date_range(group['date'].min(), group['date'].max())
    nav_s = group.set_index('date')['nav'].reindex(idx).ffill()
    filled_list.append(pd.DataFrame({'date': idx, 'nav': nav_s.values, 'amfi_code': code}))

nav = pd.concat(filled_list, ignore_index=True)
nav.to_csv(os.path.join(PROC, '02_nav_history_cleaned.csv'), index=False)
print('  After :', nav.shape)


# 2. Clean investor_transactions
print('\n[2/7] Cleaning investor transactions...')
txn = pd.read_csv(os.path.join(RAW, '08_investor_transactions.csv'))
print('  Before:', txn.shape)
type_map = {
    'sip': 'SIP', 'Sip': 'SIP', 'SIP ': 'SIP',
    'lumpsum': 'Lumpsum', 'Lumpsum ': 'Lumpsum', 'LUMP': 'Lumpsum',
    'redemption': 'Redemption', 'Redeem': 'Redemption',
}
txn['transaction_type'] = txn['transaction_type'].replace(type_map)
txn = txn[txn['amount_inr'] > 0]
txn['transaction_date'] = pd.to_datetime(txn['transaction_date']).dt.date
valid_kyc = ['Verified', 'Pending', 'Rejected']
txn = txn[txn['kyc_status'].isin(valid_kyc)]
txn.to_csv(os.path.join(PROC, '08_investor_transactions_cleaned.csv'), index=False)
print('  After :', txn.shape)


# 3. Clean scheme_performance
print('\n[3/7] Cleaning scheme performance...')
perf = pd.read_csv(os.path.join(RAW, '07_scheme_performance.csv'))
print('  Before:', perf.shape)
for col in ['return_1yr_pct', 'return_3yr_pct', 'return_5yr_pct']:
    perf[col] = pd.to_numeric(perf[col], errors='coerce')
perf['is_anomaly'] = False
for col in ['return_1yr_pct', 'return_3yr_pct', 'return_5yr_pct']:
    perf.loc[(perf[col] > 1000) | (perf[col] < -100), 'is_anomaly'] = True
perf.loc[(perf['expense_ratio_pct'] < 0.1) | (perf['expense_ratio_pct'] > 2.5), 'expense_ratio_pct'] = np.nan
perf.to_csv(os.path.join(PROC, '07_scheme_performance_cleaned.csv'), index=False)
print('  After :', perf.shape)


# 4. Copy remaining CSVs to processed
print('\n[4/7] Copying remaining files to processed...')
other = [
    '01_fund_master.csv', '03_aum_by_fund_house.csv',
    '04_monthly_sip_inflows.csv', '05_category_inflows.csv',
    '06_industry_folio_count.csv', '09_portfolio_holdings.csv',
    '10_benchmark_indices.csv'
]
for f in other:
    df = pd.read_csv(os.path.join(RAW, f))
    df.to_csv(os.path.join(PROC, f.replace('.csv', '_cleaned.csv')), index=False)
    print(f'  Saved {f.replace(".csv","_cleaned.csv")}')


# 5. Build dim_date
print('\n[5/7] Building dim_date...')
all_dates = pd.date_range(start=nav['date'].min(), end=nav['date'].max())
dim_date = pd.DataFrame({'date': all_dates})
dim_date['year']       = dim_date['date'].dt.year
dim_date['month']      = dim_date['date'].dt.month
dim_date['day']        = dim_date['date'].dt.day
dim_date['quarter']    = dim_date['date'].dt.quarter
dim_date['day_of_week']= dim_date['date'].dt.dayofweek
dim_date['is_weekend'] = dim_date['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)
dim_date['date']       = dim_date['date'].dt.date
nav['date']            = pd.to_datetime(nav['date']).dt.date
print('  dim_date rows:', len(dim_date))


# 6. Load into SQLite
print('\n[6/7] Loading into SQLite database...')
engine = create_engine(f'sqlite:///{DB}')

with open('sql/schema.sql', 'r') as f:
    schema_sql = f.read()
with engine.connect() as conn:
    for stmt in schema_sql.split(';'):
        if stmt.strip():
            conn.execute(text(stmt))
    conn.commit()

fund_df = pd.read_csv(os.path.join(RAW, '01_fund_master.csv'))
aum_df  = pd.read_csv(os.path.join(RAW, '03_aum_by_fund_house.csv'))
exclude = ['is_anomaly', 'scheme_name', 'fund_house', 'category', 'plan']
perf_cols = [c for c in perf.columns if c not in exclude]

fund_df.to_sql('dim_fund',          engine, if_exists='replace', index=False)
dim_date.to_sql('dim_date',         engine, if_exists='replace', index=False)
nav[['amfi_code','date','nav']].to_sql('fact_nav', engine, if_exists='replace', index=False)
txn.to_sql('fact_transactions',     engine, if_exists='replace', index=False)
perf[perf_cols].to_sql('fact_performance', engine, if_exists='replace', index=False)
aum_df.to_sql('fact_aum',           engine, if_exists='replace', index=False)
print('  All tables loaded.')


# 7. Verify row counts
print('\n[7/7] Verifying row counts...')
tables = ['dim_fund', 'dim_date', 'fact_nav', 'fact_transactions', 'fact_performance', 'fact_aum']
with engine.connect() as conn:
    for table in tables:
        count = pd.read_sql(f'SELECT COUNT(*) as cnt FROM {table}', conn).iloc[0]['cnt']
        print(f'  {table:<25} {count:>8} rows')

print()
print('Day 2 Complete!')
print('Git commit: "Day 2: Cleaned data + SQLite DB loaded"')
