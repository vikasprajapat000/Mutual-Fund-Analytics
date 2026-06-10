"""
╔══════════════════════════════════════════════════════════════╗
║       MUTUAL FUND RECOMMENDER — Day 6 Advanced Analytics     ║
║       Recommend top funds based on investor risk appetite     ║
╚══════════════════════════════════════════════════════════════╝

Usage:
    python recommender.py

Inputs:
    Risk appetite (Low / Moderate / Moderately High / High / Very High)

Output:
    Top 3 recommended funds with Sharpe Ratio and Category
"""

import pandas as pd
import os
import sys

# ── Paths ────────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH  = os.path.join(SCRIPT_DIR, 'data', 'processed', 'fund_master_cleaned.csv')
SC_PATH    = os.path.join(SCRIPT_DIR, 'reports', 'fund_scorecard.csv')

VALID_RISK_GRADES = ['Low', 'Moderate', 'Moderately High', 'High', 'Very High']


def load_data():
    """Load fund master and scorecard, then merge on amfi_code."""
    fund_master = pd.read_csv(DATA_PATH)
    scorecard   = pd.read_csv(SC_PATH)

    # Use one row per fund (prefer Regular plan)
    fm_dedup = (
        fund_master
        .assign(_is_regular=fund_master['scheme_name'].str.lower().str.contains('regular'))
        .sort_values('_is_regular', ascending=False)
        .drop_duplicates('amfi_code')
        [['amfi_code', 'risk_category', 'scheme_name', 'fund_house', 'category']]
    )

    merged = scorecard.merge(fm_dedup[['amfi_code', 'risk_category']], on='amfi_code', how='left')
    merged['risk_grade'] = merged['risk_category'].fillna('Moderate')

    # Derive a clean display name
    merged['display_name'] = merged.get('fund_name', merged.get('scheme_name', merged['amfi_code'].astype(str)))
    merged['display_name'] = (
        merged['display_name']
        .str.replace(r'\s*-\s*Regular\s*-\s*Growth', '', regex=True)
        .str.replace(r'\s*-\s*Direct\s*-\s*Growth', '', regex=True)
        .str.replace(r'\s*-\s*Growth', '', regex=True)
        .str.strip()
    )

    return merged


def recommend_funds(risk_input: str, df: pd.DataFrame, top_n: int = 3) -> None:
    """
    Filter funds by risk grade and recommend top N by Sharpe Ratio.

    Parameters
    ----------
    risk_input : str
        One of: Low | Moderate | Moderately High | High | Very High
    df         : pd.DataFrame
        Merged fund data with risk_grade and sharpe_ratio columns.
    top_n      : int
        Number of funds to recommend (default = 3).
    """
    # Normalise input — case-insensitive match
    matched_grade = None
    for grade in VALID_RISK_GRADES:
        if risk_input.strip().lower() == grade.lower():
            matched_grade = grade
            break

    if matched_grade is None:
        print(f'\n  ❌  Unknown risk grade: "{risk_input}"')
        print(f'  Available grades: {", ".join(VALID_RISK_GRADES)}')
        return

    filtered = df[df['risk_grade'].str.lower() == matched_grade.lower()].copy()
    filtered = filtered.sort_values('sharpe_ratio', ascending=False).head(top_n)

    if filtered.empty:
        print(f'\n  ⚠️  No funds found for risk grade: {matched_grade}')
        return

    # ── Display recommendations ───────────────────────────────────────────────
    banner = f'  Risk Appetite = {matched_grade}'
    print()
    print('  ' + '═' * 52)
    print(banner)
    print('  ' + '─' * 52)
    print(f'  {"#":<3}  {"Fund Name":<36}  {"Sharpe":>6}')
    print('  ' + '─' * 52)
    for rank, (_, row) in enumerate(filtered.iterrows(), 1):
        sharpe_str = f'{row["sharpe_ratio"]:.3f}' if pd.notna(row['sharpe_ratio']) else 'N/A'
        print(f'  {rank:<3}  {row["display_name"][:35]:<36}  {sharpe_str:>6}')
        cat = row.get('category', 'N/A')
        print(f'       Category: {cat}')
    print('  ' + '═' * 52)


def main():
    print()
    print('  ╔══════════════════════════════════════════╗')
    print('  ║   🎯  MUTUAL FUND RECOMMENDER SYSTEM     ║')
    print('  ║      Based on Risk Appetite & Sharpe     ║')
    print('  ╚══════════════════════════════════════════╝')

    # ── Load data ─────────────────────────────────────────────────────────────
    try:
        df = load_data()
    except FileNotFoundError as exc:
        print(f'\n  ❌  Data file not found: {exc}')
        print('  Please run this script from the project root directory.')
        sys.exit(1)

    print(f'\n  ✅  Loaded {len(df)} funds from scorecard')
    print(f'  Risk grades available: {", ".join(VALID_RISK_GRADES)}')

    # ── Interactive loop ──────────────────────────────────────────────────────
    while True:
        print()
        risk = input('  Enter risk appetite (or "quit" to exit): ').strip()

        if risk.lower() in ('quit', 'exit', 'q'):
            print('\n  Goodbye! Happy investing 🚀\n')
            break

        recommend_funds(risk, df)


if __name__ == '__main__':
    main()
