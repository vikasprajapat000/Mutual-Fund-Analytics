-- queries.sql
-- 10 Analytical SQL Queries

-- 1. Top 5 funds by AUM
SELECT 
    f.scheme_name, 
    f.fund_house, 
    p.aum_crore
FROM dim_fund f
JOIN fact_performance p ON f.amfi_code = p.amfi_code
ORDER BY p.aum_crore DESC
LIMIT 5;

-- 2. Average NAV per month for a specific fund (e.g., SBI Bluechip Fund, assuming amfi_code = 119551)
SELECT 
    d.year, 
    d.month, 
    AVG(n.nav) as avg_nav
FROM fact_nav n
JOIN dim_date d ON n.date = d.date
WHERE n.amfi_code = 119551
GROUP BY d.year, d.month
ORDER BY d.year, d.month;

-- 3. SIP YoY Growth (Total amount invested via SIP per year)
SELECT 
    d.year, 
    SUM(t.amount_inr) as total_sip_amount
FROM fact_transactions t
JOIN dim_date d ON t.transaction_date = d.date
WHERE t.transaction_type = 'SIP'
GROUP BY d.year
ORDER BY d.year;

-- 4. Transactions by State (Total amount and count)
SELECT 
    state, 
    COUNT(transaction_id) as total_transactions,
    SUM(amount_inr) as total_amount
FROM fact_transactions
GROUP BY state
ORDER BY total_amount DESC;

-- 5. Funds with expense_ratio < 1%
SELECT 
    scheme_name, 
    category, 
    expense_ratio_pct
FROM dim_fund
WHERE expense_ratio_pct < 1.0
ORDER BY expense_ratio_pct ASC;

-- 6. Top 5 states for SIP investments
SELECT 
    state, 
    SUM(amount_inr) as total_sip_investment
FROM fact_transactions
WHERE transaction_type = 'SIP'
GROUP BY state
ORDER BY total_sip_investment DESC
LIMIT 5;

-- 7. Best performing funds (by 1-year return) in 'Large Cap' category
SELECT 
    f.scheme_name, 
    p.return_1yr_pct
FROM dim_fund f
JOIN fact_performance p ON f.amfi_code = p.amfi_code
WHERE f.sub_category = 'Large Cap'
ORDER BY p.return_1yr_pct DESC
LIMIT 5;

-- 8. Most preferred payment mode
SELECT 
    payment_mode, 
    COUNT(*) as num_transactions
FROM fact_transactions
GROUP BY payment_mode
ORDER BY num_transactions DESC;

-- 9. Number of transactions per city tier
SELECT 
    city_tier, 
    COUNT(*) as transaction_count, 
    SUM(amount_inr) as total_investment
FROM fact_transactions
GROUP BY city_tier
ORDER BY total_investment DESC;

-- 10. Risk Category distribution of funds
SELECT 
    risk_category, 
    COUNT(amfi_code) as total_funds
FROM dim_fund
GROUP BY risk_category
ORDER BY total_funds DESC;
