"""
Day 6 — Advanced Analytics Runner
Generates: var_cvar_report.csv, rolling_sharpe_chart.png
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

plt.style.use('seaborn-v0_8-darkgrid')

import os
BASE_DATA = r'd:\Mutual Fund Analytic\Mutual-Fund-Analytics\data\processed' + '\\'
BASE_RPT  = r'd:\Mutual Fund Analytic\Mutual-Fund-Analytics\reports' + '\\'
os.makedirs(BASE_RPT, exist_ok=True)
BASE_RPT_PLOT = BASE_RPT

# ── Load data ────────────────────────────────────────────────────────────────
print('Loading data...')
nav_df      = pd.read_csv(BASE_DATA + 'nav_history_cleaned.csv',          parse_dates=['date'])
fund_master = pd.read_csv(BASE_DATA + 'fund_master_cleaned.csv')
scorecard_path = os.path.join(r'd:\Mutual Fund Analytic\Mutual-Fund-Analytics\reports', 'fund_scorecard.csv')
scorecard   = pd.read_csv(scorecard_path)

# Fund lookup table
fund_lookup = scorecard[['amfi_code','scheme_name']].copy()
fund_lookup.columns = ['amfi_code', 'scheme_name']
fm_lookup   = fund_master[['amfi_code','scheme_name']].drop_duplicates('amfi_code')
fund_lookup = (
    fund_lookup.set_index('amfi_code')
    .combine_first(fm_lookup.set_index('amfi_code'))
    .reset_index()
)
print('Data loaded.')

# ── SECTION 1: VaR & CVaR ───────────────────────────────────────────────────
print('\nComputing VaR & CVaR for all funds...')
nav_df = nav_df.sort_values(['amfi_code','date'])
nav_df['daily_return'] = nav_df.groupby('amfi_code')['nav'].pct_change()

results = []
for fund in nav_df['amfi_code'].unique():
    returns = nav_df[nav_df['amfi_code'] == fund]['daily_return'].dropna()
    if len(returns) < 20:
        continue
    var  = np.percentile(returns, 5)
    cvar = returns[returns <= var].mean()

    name_rows = fund_lookup[fund_lookup['amfi_code'] == fund]
    fund_name = name_rows['scheme_name'].values[0] if len(name_rows) > 0 else str(fund)

    results.append({
        'amfi_code' : fund,
        'Fund Name' : fund_name,
        'VaR (95%)' : round(var,  4),
        'CVaR'      : round(cvar, 4),
    })

var_cvar_df = (
    pd.DataFrame(results)
    .sort_values('VaR (95%)', ascending=True)
    .reset_index(drop=True)
)
var_cvar_df.to_csv(BASE_RPT + 'var_cvar_report.csv', index=False)
print('Saved: reports/var_cvar_report.csv')
print(var_cvar_df[['Fund Name','VaR (95%)','CVaR']].head(5).to_string(index=False))

# ── SECTION 2: Rolling Sharpe ────────────────────────────────────────────────
print('\nComputing Rolling Sharpe Ratio...')

# Keyword search for 5 target funds
kw_map = {
    'SBI Bluechip'    : ['sbi',    'bluechip'],
    'ICICI Bluechip'  : ['icici',  'bluechip'],
    'Axis Bluechip'   : ['axis',   'bluechip'],
    'Kotak Bluechip'  : ['kotak',  'bluechip'],
    'Nippon Large Cap': ['nippon', 'large'],
}

selected_funds = {}
for label, keywords in kw_map.items():
    mask = fund_lookup['scheme_name'].str.lower().apply(
        lambda x: all(k in x for k in keywords)
    )
    matches = fund_lookup[mask]
    reg     = matches[matches['scheme_name'].str.lower().str.contains('regular')]
    chosen  = reg.iloc[0] if len(reg) > 0 else (matches.iloc[0] if len(matches) > 0 else None)
    if chosen is not None:
        selected_funds[label] = int(chosen['amfi_code'])
        print(f'  [{label}] -> {int(chosen["amfi_code"])} | {chosen["scheme_name"]}')

# Fallback: use top Sharpe funds if fewer than 5 matched
if len(selected_funds) < 5:
    top_sc = scorecard.nlargest(8, 'sharpe_ratio')
    for _, row in top_sc.iterrows():
        if int(row['amfi_code']) not in selected_funds.values():
            lbl = str(row.get('fund_name', row['amfi_code']))[:20]
            selected_funds[lbl] = int(row['amfi_code'])
            print(f'  [Fallback] -> {int(row["amfi_code"])} | {lbl}')
        if len(selected_funds) == 5:
            break

print(f'Using {len(selected_funds)} funds for Rolling Sharpe chart.')

colors = plt.cm.tab10(np.linspace(0, 1, len(selected_funds)))
fig, ax = plt.subplots(figsize=(14, 6))

best_fund_label  = None
best_mean_sharpe = -np.inf

for (label, code), color in zip(selected_funds.items(), colors):
    fund_rets = nav_df[nav_df['amfi_code'] == code].set_index('date')['daily_return'].dropna()
    roll_mean   = fund_rets.rolling(90).mean()
    roll_std    = fund_rets.rolling(90).std()
    roll_sharpe = (roll_mean / roll_std) * np.sqrt(252)
    roll_sharpe = roll_sharpe.dropna()

    ax.plot(roll_sharpe.index, roll_sharpe.values,
            label=label, color=color, linewidth=2, alpha=0.88)

    mean_val = roll_sharpe.mean()
    if mean_val > best_mean_sharpe:
        best_mean_sharpe = mean_val
        best_fund_label  = label

ax.axhline(0, color='black', linewidth=0.8, linestyle='--', alpha=0.5, label='Zero Line')
ax.set_title('Rolling Sharpe Ratio — 90-Day Window (Annualised)', fontsize=14, fontweight='bold')
ax.set_xlabel('Date', fontsize=12)
ax.set_ylabel('Sharpe Ratio', fontsize=12)
ax.legend(fontsize=10, loc='upper left', framealpha=0.9)
ax.tick_params(axis='x', rotation=30)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(BASE_RPT_PLOT, 'rolling_sharpe_chart.png'), dpi=150, bbox_inches='tight')
plt.close()
print('Saved: reports/rolling_sharpe_chart.png')
print(f'Best avg Rolling Sharpe -> {best_fund_label} ({best_mean_sharpe:.3f})')

print('\nAll Day 6 outputs generated successfully.')
