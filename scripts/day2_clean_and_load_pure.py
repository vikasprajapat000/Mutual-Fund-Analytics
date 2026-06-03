import csv
import sqlite3
import os
from datetime import datetime, timedelta

# File paths
DATA_DIR = 'data'
RAW_DIR = os.path.join(DATA_DIR, 'raw')
PROC_DIR = os.path.join(DATA_DIR, 'processed')
DB_DIR = os.path.join(DATA_DIR, 'db')
DB_PATH = os.path.join(DB_DIR, 'bluestock_mf.db')
SCHEMA_PATH = 'sql/schema.sql'

os.makedirs(PROC_DIR, exist_ok=True)
os.makedirs(DB_DIR, exist_ok=True)

print("Starting Day 2 Data Cleaning (Pure Python Mode)...")

def safe_float(val):
    try:
        return float(val)
    except:
        return None

# ==========================================
# 1. Clean nav_history.csv
# ==========================================
print("\nCleaning 02_nav_history.csv...")
nav_records = {}
min_max_dates = {}
orig_nav_count = 0

with open(os.path.join(RAW_DIR, '02_nav_history.csv'), 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        orig_nav_count += 1
        amfi_code = row['amfi_code']
        date_str = row['date']
        nav_val = safe_float(row['nav'])
        
        if nav_val is not None and nav_val > 0:
            dt = datetime.strptime(date_str, '%Y-%m-%d').date()
            nav_records[(amfi_code, dt)] = nav_val
            
            if amfi_code not in min_max_dates:
                min_max_dates[amfi_code] = [dt, dt]
            else:
                if dt < min_max_dates[amfi_code][0]: min_max_dates[amfi_code][0] = dt
                if dt > min_max_dates[amfi_code][1]: min_max_dates[amfi_code][1] = dt

print(f"Original nav rows: {orig_nav_count}")

# Ffill missing dates and write to processed
cleaned_nav_count = 0
all_dates = set()
with open(os.path.join(PROC_DIR, '02_nav_history_cleaned.csv'), 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['amfi_code', 'date', 'nav'])
    
    for amfi_code, (min_dt, max_dt) in min_max_dates.items():
        curr_dt = min_dt
        last_nav = None
        while curr_dt <= max_dt:
            all_dates.add(curr_dt)
            if (amfi_code, curr_dt) in nav_records:
                last_nav = nav_records[(amfi_code, curr_dt)]
            
            if last_nav is not None:
                writer.writerow([amfi_code, curr_dt.strftime('%Y-%m-%d'), last_nav])
                cleaned_nav_count += 1
            curr_dt += timedelta(days=1)

print(f"Cleaned nav rows (after ffill): {cleaned_nav_count}")

# Generate dim_date from all_dates
dim_date_records = []
for dt in sorted(list(all_dates)):
    dim_date_records.append([
        dt.strftime('%Y-%m-%d'),
        dt.year, dt.month, dt.day,
        (dt.month - 1) // 3 + 1,
        dt.weekday(),
        1 if dt.weekday() >= 5 else 0
    ])

# ==========================================
# 2. Clean investor_transactions.csv
# ==========================================
print("\nCleaning 08_investor_transactions.csv...")
type_map = {
    'sip': 'SIP', 'Sip': 'SIP', 'systematic investment plan': 'SIP',
    'lumpsum': 'Lumpsum', 'LUMP': 'Lumpsum', 'One Time': 'Lumpsum',
    'redemption': 'Redemption', 'Redeem': 'Redemption', 'Withdraw': 'Redemption'
}
valid_kyc = {'Verified', 'Pending', 'Rejected'}
cleaned_txn_count = 0
orig_txn_count = 0

with open(os.path.join(RAW_DIR, '08_investor_transactions.csv'), 'r', encoding='utf-8') as fin, \
     open(os.path.join(PROC_DIR, '08_investor_transactions_cleaned.csv'), 'w', newline='', encoding='utf-8') as fout:
    
    reader = csv.DictReader(fin)
    writer = csv.DictWriter(fout, fieldnames=reader.fieldnames)
    writer.writeheader()
    
    for row in reader:
        orig_txn_count += 1
        t_type = row.get('transaction_type', '')
        row['transaction_type'] = type_map.get(t_type, t_type)
        
        amt = safe_float(row.get('amount_inr', 0))
        
        # fix date formats
        try:
            # handle formats if any variance, here we assume standard format or basic parsing
            # Some dates might be like DD/MM/YYYY, let's try standardizing to YYYY-MM-DD
            raw_dt = row['transaction_date']
            if '/' in raw_dt:
                dt_parts = raw_dt.split('/')
                if len(dt_parts[0]) == 4:
                    parsed_dt = datetime.strptime(raw_dt, '%Y/%m/%d').date()
                else:
                    parsed_dt = datetime.strptime(raw_dt, '%d/%m/%Y').date()
            else:
                parsed_dt = datetime.strptime(raw_dt, '%Y-%m-%d').date()
            row['transaction_date'] = parsed_dt.strftime('%Y-%m-%d')
        except:
            pass # leave as is if unparseable
            
        kyc = row.get('kyc_status', '')
        
        if amt is not None and amt > 0 and kyc in valid_kyc:
            writer.writerow(row)
            cleaned_txn_count += 1

print(f"Original txn rows: {orig_txn_count}, Cleaned: {cleaned_txn_count}")

# ==========================================
# 3. Clean scheme_performance.csv
# ==========================================
print("\nCleaning 07_scheme_performance.csv...")
return_cols = ['return_1yr_pct', 'return_3yr_pct', 'return_5yr_pct']
orig_perf_count = 0
cleaned_perf_count = 0

with open(os.path.join(RAW_DIR, '07_scheme_performance.csv'), 'r', encoding='utf-8') as fin, \
     open(os.path.join(PROC_DIR, '07_scheme_performance_cleaned.csv'), 'w', newline='', encoding='utf-8') as fout:
     
    reader = csv.DictReader(fin)
    fieldnames = reader.fieldnames + ['is_anomaly'] if 'is_anomaly' not in reader.fieldnames else reader.fieldnames
    writer = csv.DictWriter(fout, fieldnames=fieldnames)
    writer.writeheader()
    
    for row in reader:
        orig_perf_count += 1
        is_anomaly = False
        for c in return_cols:
            val = safe_float(row.get(c, ''))
            if val is not None:
                if val > 1000 or val < -100:
                    is_anomaly = True
                row[c] = val
            else:
                row[c] = ''
                
        row['is_anomaly'] = str(is_anomaly)
        
        er = safe_float(row.get('expense_ratio_pct', ''))
        if er is not None and (er < 0.1 or er > 2.5):
            row['expense_ratio_pct'] = ''
            
        writer.writerow(row)
        cleaned_perf_count += 1

print(f"Original perf rows: {orig_perf_count}, Cleaned: {cleaned_perf_count}")

# ==========================================
# 4. Copy remaining datasets
# ==========================================
print("\nProcessing remaining datasets...")
other_files = [
    '01_fund_master.csv', '03_aum_by_fund_house.csv', '04_monthly_sip_inflows.csv',
    '05_category_inflows.csv', '06_industry_folio_count.csv', '09_portfolio_holdings.csv',
    '10_benchmark_indices.csv'
]

for file in other_files:
    in_path = os.path.join(RAW_DIR, file)
    out_path = os.path.join(PROC_DIR, file.replace('.csv', '_cleaned.csv'))
    with open(in_path, 'r', encoding='utf-8') as fin, open(out_path, 'w', newline='', encoding='utf-8') as fout:
        reader = csv.reader(fin)
        writer = csv.writer(fout)
        for row in reader:
            writer.writerow(row)

# ==========================================
# 5. Load datasets into SQLite
# ==========================================
print("\nLoading data into SQLite...")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Execute schema
with open(SCHEMA_PATH, 'r') as f:
    cursor.executescript(f.read())

def load_csv_to_sqlite(table_name, csv_path, skip_columns=None):
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        
        # remove skipped columns from headers
        if skip_columns:
            keep_indices = [i for i, h in enumerate(headers) if h not in skip_columns]
            headers = [headers[i] for i in keep_indices]
        else:
            keep_indices = list(range(len(headers)))
            
        placeholders = ','.join(['?'] * len(headers))
        query = f"INSERT INTO {table_name} ({','.join(headers)}) VALUES ({placeholders})"
        
        batch = []
        for row in reader:
            filtered_row = [row[i] if row[i] != '' else None for i in keep_indices]
            batch.append(filtered_row)
            if len(batch) >= 10000:
                cursor.executemany(query, batch)
                batch = []
        if batch:
            cursor.executemany(query, batch)
        conn.commit()

# Loading dim_fund
load_csv_to_sqlite('dim_fund', os.path.join(PROC_DIR, '01_fund_master_cleaned.csv'))

# Loading dim_date
query = "INSERT INTO dim_date (date, year, month, day, quarter, day_of_week, is_weekend) VALUES (?,?,?,?,?,?,?)"
cursor.executemany(query, dim_date_records)
conn.commit()

# Loading fact_nav
load_csv_to_sqlite('fact_nav', os.path.join(PROC_DIR, '02_nav_history_cleaned.csv'))

# Loading fact_transactions
load_csv_to_sqlite('fact_transactions', os.path.join(PROC_DIR, '08_investor_transactions_cleaned.csv'))

# Loading fact_performance
load_csv_to_sqlite('fact_performance', os.path.join(PROC_DIR, '07_scheme_performance_cleaned.csv'), skip_columns=['is_anomaly', 'scheme_name', 'fund_house', 'category', 'plan'])

# Loading fact_aum
load_csv_to_sqlite('fact_aum', os.path.join(PROC_DIR, '03_aum_by_fund_house_cleaned.csv'))

# Verify counts
tables = ['dim_fund', 'dim_date', 'fact_nav', 'fact_transactions', 'fact_performance', 'fact_aum']
for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"Table {table}: {count} rows")

conn.close()
print("\nDay 2 Tasks Finished Successfully!")
