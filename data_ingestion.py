import pandas as pd
import os

RAW = os.path.join('data', 'raw')

files = {
    'Fund Master'        : '01_fund_master.csv',
    'NAV History'        : '02_nav_history.csv',
    'AUM by Fund House'  : '03_aum_by_fund_house.csv',
    'Monthly SIP Inflows': '04_monthly_sip_inflows.csv',
    'Category Inflows'   : '05_category_inflows.csv',
    'Industry Folio Count': '06_industry_folio_count.csv',
    'Scheme Performance' : '07_scheme_performance.csv',
    'Investor Transactions': '08_investor_transactions.csv',
    'Portfolio Holdings' : '09_portfolio_holdings.csv',
    'Benchmark Indices'  : '10_benchmark_indices.csv',
}

for name, filename in files.items():
    path = os.path.join(RAW, filename)
    print('=' * 60)
    print(name)
    print('=' * 60)
    try:
        df = pd.read_csv(path)
        print('Shape       :', df.shape)
        print('Columns     :', df.columns.tolist())
        print('Dtypes:\n',    df.dtypes)
        print('Head:\n',      df.head(3).to_string())
        print('Missing:\n',   df.isnull().sum().to_string())
    except Exception as e:
        print('Error:', e)
    print()