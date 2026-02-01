import pyodbc
import yfinance as yf
import pandas as pd
from datetime import date

USD_INR = 91.68   # approx rate

start_date = "2026-01-01"
end_date = date.today().strftime("%Y-%m-%d")

# Fetch data
gold_df = yf.download("GC=F", start=start_date, end=end_date)
silver_df = yf.download("SI=F", start=start_date, end=end_date)

# SQL connect
conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost\\SQLEXPRESS;"
    "DATABASE=GoldSilverDB;"
    "Trusted_Connection=yes;"
)
cursor = conn.cursor()

for d in gold_df.index:

    gold_usd = float(gold_df.loc[d]["Close"].iloc[0])
    silver_usd = float(silver_df.loc[d]["Close"].iloc[0])

    # Convert to Indian units
    gold_inr_10g = gold_usd * USD_INR / 31.1 * 10
    silver_inr_kg = silver_usd * USD_INR / 31.1 * 1000

    # Avoid duplicates
    cursor.execute(
        "SELECT COUNT(*) FROM DailyPrices WHERE PriceDate = ?", d.date()
    )

    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO DailyPrices VALUES (?, ?, ?)",
            d.date(), gold_inr_10g, silver_inr_kg
        )

conn.commit()
conn.close()

print("FULL DATA FROM JAN 1 TO TODAY SAVED SUCCESSFULLY!")