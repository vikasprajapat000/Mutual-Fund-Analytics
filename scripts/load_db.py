
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import create_engine

engine = create_engine(
    "sqlite:///data/db/bluestock_mf.db"
)

fund = pd.read_csv(
    "data/processed/fund_master_clean.csv"
)

fund.to_sql(
    "dim_fund",
    engine,
    if_exists="replace",
    index=False
)

print("Database Created Successfully")