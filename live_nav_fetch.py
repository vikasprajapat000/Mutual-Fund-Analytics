import requests
import pandas as pd
import os

RAW = os.path.join('data', 'raw')
os.makedirs(RAW, exist_ok=True)

print('Fetching Live NAV from mfapi.in...')
print()

url = 'https://api.mfapi.in/mf/125497'
try:
    response = requests.get(url, timeout=10)
    data     = response.json()
    nav_df   = pd.DataFrame(data['data'])
    nav_df.to_csv(os.path.join(RAW, 'hdfc_top100_live_nav.csv'), index=False)
    print('HDFC Top 100 NAV fetched')
    print('Scheme  :', data.get('meta', {}).get('scheme_name', 'N/A'))
    print('Records :', len(nav_df))
    print(nav_df.head(3).to_string())
except Exception as e:
    print('Error fetching HDFC Top 100:', e)

print()

funds = {
    'SBI_Bluechip'     : 119551,
    'ICICI_Bluechip'   : 120503,
    'Nippon_Large_Cap' : 118632,
    'Axis_Bluechip'    : 119092,
    'Kotak_Bluechip'   : 120841,
}

for name, code in funds.items():
    try:
        url      = f'https://api.mfapi.in/mf/{code}'
        response = requests.get(url, timeout=10)
        data     = response.json()
        nav_df   = pd.DataFrame(data['data'])
        save_path = os.path.join(RAW, f'{name}.csv')
        nav_df.to_csv(save_path, index=False)
        print(f'Saved {name}.csv  ({len(nav_df)} rows)')
    except Exception as e:
        print(f'Error fetching {name}: {e}')

print()
print('Live NAV fetch complete.')