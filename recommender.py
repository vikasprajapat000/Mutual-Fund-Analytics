"""
Mutual Fund Recommender System - Day 6 Advanced Analytics
This module provides a command-line interface to recommend top-performing mutual funds
by matching user risk appetites with their 3-year risk-adjusted returns (Sharpe Ratio).

Usage:
    python recommender.py
"""

import os
import sys
import pandas as pd

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(SCRIPT_DIR, "data", "processed", "fund_master_cleaned.csv")
SC_PATH = os.path.join(SCRIPT_DIR, "reports", "fund_scorecard.csv")

VALID_RISK_GRADES = ["Low", "Moderate", "Moderately High", "High", "Very High"]


def load_data() -> pd.DataFrame:
    """
    Load fund master list and scorecard rankings, then merge them on amfi_code.
    
    Returns:
        pd.DataFrame: Merged dataframe containing schemes, risk categories,
                      and calculated performance metrics (Sharpe ratio, etc.).
    """
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Missing master cleaned data at: {DATA_PATH}")
    if not os.path.exists(SC_PATH):
        raise FileNotFoundError(f"Missing performance scorecard at: {SC_PATH}")

    fund_master = pd.read_csv(DATA_PATH)
    scorecard = pd.read_csv(SC_PATH)

    # De-duplicate fund master preferring 'Regular' plans for retail focus
    fund_master["is_regular"] = fund_master["scheme_name"].str.lower().str.contains("regular")
    fm_dedup = (
        fund_master
        .sort_values("is_regular", ascending=False)
        .drop_duplicates("amfi_code")
        [["amfi_code", "risk_category", "scheme_name", "fund_house", "category"]]
    )

    merged = scorecard.merge(fm_dedup[["amfi_code", "risk_category"]], on="amfi_code", how="left")
    merged["risk_grade"] = merged["risk_category"].fillna("Moderate")

    # Clean fund display name (strip regular/direct growth suffixes)
    merged["display_name"] = merged.get("fund_name", merged.get("scheme_name", merged["amfi_code"].astype(str)))
    merged["display_name"] = (
        merged["display_name"]
        .str.replace(r"\s*-\s*Regular\s*-\s*Growth", "", regex=True)
        .str.replace(r"\s*-\s*Direct\s*-\s*Growth", "", regex=True)
        .str.replace(r"\s*-\s*Growth", "", regex=True)
        .str.strip()
    )

    return merged


def recommend_funds(risk_input: str, df: pd.DataFrame, top_n: int = 3) -> None:
    """
    Filter schemes by risk level and recommend the top N funds ranked by Sharpe ratio.

    Args:
        risk_input (str): User input for risk appetite.
        df (pd.DataFrame): Dataframe of funds containing risk and performance metrics.
        top_n (int, optional): Number of recommendations to display. Defaults to 3.
    """
    matched_grade = None
    for grade in VALID_RISK_GRADES:
        if risk_input.strip().lower() == grade.lower():
            matched_grade = grade
            break

    if matched_grade is None:
        print(f"\n  [ERROR] Unknown risk grade: '{risk_input}'")
        print(f"  Supported options: {', '.join(VALID_RISK_GRADES)}")
        return

    # Filter and sort by risk-adjusted return (Sharpe Ratio)
    filtered = df[df["risk_grade"].str.lower() == matched_grade.lower()].copy()
    filtered = filtered.sort_values("sharpe_ratio", ascending=False).head(top_n)

    if filtered.empty:
        print(f"\n  [WARNING] No mutual funds found in database matching risk grade: {matched_grade}")
        return

    # Print recommendations banner
    print()
    print("  " + "=" * 52)
    print(f"  Risk Appetite: {matched_grade}")
    print("  " + "-" * 52)
    print(f"  {'#':<3}  {'Fund Name':<36}  {'Sharpe':>6}")
    print("  " + "-" * 52)
    
    for rank, (_, row) in enumerate(filtered.iterrows(), 1):
        sharpe_str = f"{row['sharpe_ratio']:.3f}" if pd.notna(row["sharpe_ratio"]) else "N/A"
        print(f"  {rank:<3}  {row['display_name'][:35]:<36}  {sharpe_str:>6}")
        cat = row.get("category", "N/A")
        print(f"       Category: {cat}")
        
    print("  " + "=" * 52)


def main() -> None:
    """Main program execution loop for fund recommendations."""
    print()
    print("  +------------------------------------------+")
    print("  |   [TARGET] MUTUAL FUND RECOMMENDER SYSTEM |")
    print("  |      Based on Risk Appetite & Sharpe     |")
    print("  +------------------------------------------+")

    try:
        df = load_data()
    except FileNotFoundError as exc:
        print(f"\n  [ERROR] Data load failed: {exc}")
        print("  Please check database configuration and script paths.")
        sys.exit(1)

    print(f"\n  [OK] Loaded {len(df)} schemes from scorecard database.")
    print(f"  Risk levels available: {', '.join(VALID_RISK_GRADES)}")

    while True:
        try:
            print()
            risk = input("  Enter risk appetite (or 'quit' to exit): ").strip()
            if risk.lower() in ("quit", "exit", "q"):
                print("\n  Goodbye! Happy investing.\n")
                break
            if not risk:
                continue
            recommend_funds(risk, df)
        except (KeyboardInterrupt, EOFError):
            print("\n\n  Exiting recommender. Goodbye!\n")
            break


if __name__ == "__main__":
    main()
