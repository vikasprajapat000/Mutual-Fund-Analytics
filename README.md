# Mutual Fund Analytics Project

A professional data engineering and performance analysis pipeline for mutual funds. This repository contains the tools, scripts, SQL schemas, and Jupyter notebooks to ingest, clean, store, and analyze mutual fund data.

---

## 📁 Project Structure

```text
mutual-fund-analysis/
├── data/
│   ├── raw/                  # 10 Original datasets provided by the company (CSVs)
│   ├── processed/            # Cleaned CSVs generated after running scripts
│   └── db/                   # SQLite database storing the Star Schema tables
├── notebooks/
│   ├── EDA_Analysis.ipynb    # Day 3: Exploratory Data Analysis & visualizations
│   └── Performance_Analytics.ipynb # Day 4: Mutual Fund performance calculations & rankings
├── reports/
│   ├── charts/               # Detailed charts generated during EDA
│   ├── alpha_beta.csv        # Calculated alpha, beta OLS metrics
│   ├── fund_scorecard.csv    # Final 0-100 composite rankings
│   └── *.png                 # Visualizations for Sharpe, CAGR, drawdown, benchmark comparison
├── sql/
│   ├── schema.sql            # Star schema table definitions (dim_fund, fact_nav, fact_transactions, etc.)
│   └── queries.sql           # 10 analytical SQL queries for database verification
├── data_dictionary.md        # Comprehensive data dictionary for the schema tables
├── data_ingestion.py         # Day 1: Script to scan raw data files
├── live_nav_fetch.py         # Day 1: Fetching live NAV details from api.mfapi.in
├── requirements.txt          # Python dependencies with pinned versions
└── .gitignore                # Git ignore file (excluding venv, local DB, and api-fetched raw CSVs)
```

---

## 🛠️ Setup & Installation

### 1. Pre-requisites
Make sure you have Python (version 3.10+ recommended) installed on your system.

### 2. Configure Virtual Environment
Create and activate a Python virtual environment to manage dependencies cleanly:
```bash
# Create virtual environment
python -m venv venv

# Activate on Windows:
venv\Scripts\activate

# Activate on macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
Install all the required python packages using:
```bash
pip install -r requirements.txt
```

---

## 🚀 How to Run the Pipeline

### Step 1: Run Data Ingestion
Scan and review raw CSV datasets (shape, dtypes, missing values):
```bash
python data_ingestion.py
```

### Step 2: Run Live NAV Fetching (Optional Verification)
Fetch historical NAV data from the live API for reference.
*(Note: These API-fetched files are stored locally but ignored by Git to keep the repository clean of unverified/extra files).*
```bash
python live_nav_fetch.py
```

### Step 3: Run Data Cleaning & DB Loader
Clean the datasets, handle anomalies, resolve missing NAV dates with forward-filling, build a date dimension (`dim_date`), and load all tables into SQLite database (`data/db/bluestock_mf.db`):
```bash
python scripts/day2_clean_and_load.py
```

---

## 📊 Analytics & Metrics Computed (Day 4)

The calculations in [`notebooks/Performance_Analytics.ipynb`](file:///d:/mutual-fund-analysis/notebooks/Performance_Analytics.ipynb) compute the following key performance indicators for all 40 schemes:

1. **Daily Returns**: $\text{nav}_t / \text{nav}_{t-1} - 1$.
2. **CAGR**: $1\text{yr}$, $3\text{yr}$, and $5\text{yr}$ compound annual growth rates.
3. **Sharpe Ratio**: Annualized risk-adjusted return relative to risk-free rate ($R_f = 6.5\%$).
4. **Sortino Ratio**: Same as Sharpe, but using only downside standard deviation.
5. **Alpha & Beta**: Calculated using OLS regression against the **Nifty 100** benchmark.
6. **Maximum Drawdown**: Worst peak-to-trough drop and corresponding date range.
7. **Fund Scorecard (0–100)**: Composite rating based on:
   - $30\%$ $\times$ $3\text{yr}$ Return Rank
   - $25\%$ $\times$ Sharpe Rank
   - $20\%$ $\times$ Alpha Rank
   - $15\%$ $\times$ Expense Ratio Rank (inverse)
   - $10\%$ $\times$ Max Drawdown Rank (inverse)
