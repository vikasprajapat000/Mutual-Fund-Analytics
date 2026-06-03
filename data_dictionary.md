# Data Dictionary - Mutual Fund Analytics

This document contains the data dictionary for the `bluestock_mf.db` SQLite database, which forms the core of the Mutual Fund Analytics project. The database follows a Star Schema design.

## 1. Dimension Tables

### `dim_fund`
Stores master information about each mutual fund scheme.
*Source Dataset:* `01_fund_master_cleaned.csv`

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `amfi_code` | INTEGER (PK) | Unique identifier for the mutual fund assigned by AMFI. |
| `fund_house` | TEXT | The Asset Management Company (AMC) managing the fund. |
| `scheme_name` | TEXT | Full name of the mutual fund scheme. |
| `category` | TEXT | Primary category of the fund (e.g., Equity, Debt, Hybrid). |
| `sub_category` | TEXT | Secondary category classification (e.g., Large Cap, Mid Cap, Liquid). |
| `plan` | TEXT | Plan type (e.g., Direct, Regular). |
| `launch_date` | DATE | Date when the fund was launched. |
| `benchmark` | TEXT | The benchmark index against which the fund's performance is measured. |
| `expense_ratio_pct` | REAL | The annual maintenance charge levied by mutual funds. |
| `exit_load_pct` | REAL | Fee charged when withdrawing money within a specified period. |
| `min_sip_amount` | INTEGER | Minimum amount required to start a Systematic Investment Plan (SIP). |
| `min_lumpsum_amount` | INTEGER | Minimum amount required for a one-time (lumpsum) investment. |
| `fund_manager` | TEXT | Name of the person(s) managing the fund. |
| `risk_category` | TEXT | Risk classification (e.g., Low, Moderate, High, Very High). |
| `sebi_category_code` | TEXT | SEBI assigned category code. |

### `dim_date`
A standard date dimension table for time-based analysis.
*Source Dataset:* Generated from `02_nav_history_cleaned.csv` dates.

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `date` | DATE (PK) | The specific calendar date (YYYY-MM-DD). |
| `year` | INTEGER | The calendar year. |
| `month` | INTEGER | The calendar month (1-12). |
| `day` | INTEGER | The day of the month (1-31). |
| `quarter` | INTEGER | The calendar quarter (1-4). |
| `day_of_week` | INTEGER | Day of the week (0=Monday, 6=Sunday). |
| `is_weekend` | INTEGER | Boolean flag indicating if the date falls on a weekend (1=Yes, 0=No). |


## 2. Fact Tables

### `fact_nav`
Stores historical Net Asset Value (NAV) records.
*Source Dataset:* `02_nav_history_cleaned.csv`

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `id` | INTEGER (PK) | Auto-incrementing surrogate key. |
| `amfi_code` | INTEGER (FK) | Reference to `dim_fund.amfi_code`. |
| `date` | DATE (FK) | Reference to `dim_date.date`. |
| `nav` | REAL | The Net Asset Value of the fund on that specific date. |

### `fact_transactions`
Stores investor transaction records including SIPs and lumpsum investments.
*Source Dataset:* `08_investor_transactions_cleaned.csv`

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `transaction_id` | INTEGER (PK) | Auto-incrementing unique identifier for each transaction. |
| `investor_id` | TEXT | Unique identifier for the investor. |
| `transaction_date`| DATE (FK) | Date of the transaction, referring to `dim_date.date`. |
| `amfi_code` | INTEGER (FK) | Reference to `dim_fund.amfi_code`. |
| `transaction_type`| TEXT | Type of transaction (e.g., SIP, Lumpsum, Redemption). |
| `amount_inr` | REAL | Transaction amount in Indian Rupees (INR). |
| `state` | TEXT | State from which the transaction originated. |
| `city` | TEXT | City from which the transaction originated. |
| `city_tier` | TEXT | Tier classification of the city (e.g., Tier 1, Tier 2). |
| `age_group` | TEXT | Age group of the investor. |
| `gender` | TEXT | Gender of the investor. |
| `annual_income_lakh`| REAL | Investor's annual income bracket in lakhs. |
| `payment_mode` | TEXT | Mode of payment (e.g., UPI, NetBanking). |
| `kyc_status` | TEXT | KYC status (Verified, Pending, Rejected). |

### `fact_performance`
Stores performance metrics, risk ratios, and ratings for each fund.
*Source Dataset:* `07_scheme_performance_cleaned.csv`

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `amfi_code` | INTEGER (PK) | Reference to `dim_fund.amfi_code`. |
| `return_1yr_pct` | REAL | 1-year annualized return percentage. |
| `return_3yr_pct` | REAL | 3-year annualized return percentage. |
| `return_5yr_pct` | REAL | 5-year annualized return percentage. |
| `benchmark_3yr_pct` | REAL | Benchmark's 3-year annualized return percentage. |
| `alpha` | REAL | Measure of the active return on an investment. |
| `beta` | REAL | Measure of the volatility of a security compared to the market. |
| `sharpe_ratio` | REAL | Measure of risk-adjusted return. |
| `sortino_ratio` | REAL | Variation of Sharpe ratio focusing on downside risk. |
| `std_dev_ann_pct` | REAL | Annualized standard deviation of returns. |
| `max_drawdown_pct` | REAL | Maximum observed loss from a peak to a trough. |
| `aum_crore` | REAL | Assets Under Management in Crores. |
| `expense_ratio_pct` | REAL | Expense ratio percentage of the fund. |
| `morningstar_rating`| INTEGER | Rating provided by Morningstar (out of 5). |
| `risk_grade` | TEXT | Grade assigned based on the fund's risk metrics. |

### `fact_aum`
Stores Assets Under Management (AUM) details by fund house over time.
*Source Dataset:* `03_aum_by_fund_house_cleaned.csv`

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `id` | INTEGER (PK) | Auto-incrementing surrogate key. |
| `date` | DATE (FK) | Reference to `dim_date.date`. |
| `fund_house` | TEXT | Name of the Asset Management Company (AMC). |
| `aum_lakh_crore` | REAL | AUM represented in Lakh Crores. |
| `aum_crore` | REAL | AUM represented in Crores. |
| `num_schemes` | INTEGER | Number of mutual fund schemes managed by the AMC. |
