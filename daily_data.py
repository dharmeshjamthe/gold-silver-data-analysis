import pyodbc
import yfinance as yf
import requests
from datetime import date

# ---------- SQL CONNECTION ----------
conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost\\SQLEXPRESS;"
    "DATABASE=GoldSilverDB;"
    "Trusted_Connection=yes;"
)
cursor = conn.cursor()

# ---------- USD TO INR ----------
fx = requests.get("https://api.exchangerate-api.com/v4/latest/USD").json()
USD_INR = fx["rates"]["INR"]

print("Live USD-INR Rate:", USD_INR)

# ---------- DOWNLOAD FULL DATA ----------
gold_df = yf.download("GC=F", start="2026-01-01")
silver_df = yf.download("SI=F", start="2026-01-01")

gold_df = gold_df.dropna()
silver_df = silver_df.dropna()

# ---------- LOOP & INSERT ----------
for d in gold_df.index:
    price_date = d.date()

    gold_usd = float(gold_df.loc[d]["Close"])
    silver_usd = float(silver_df.loc[d]["Close"])

    # Convert to Indian units
    gold_inr = gold_usd * USD_INR / 31.1 * 10     # ₹ per 10g
    silver_inr = silver_usd * USD_INR / 31.1 * 1000  # ₹ per kg

    # Avoid duplicates
    cursor.execute(
        "SELECT COUNT(*) FROM DailyPrices WHERE PriceDate = ?", price_date
    )
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO DailyPrices (PriceDate, GoldPrice, SilverPrice) VALUES (?, ?, ?)",
            price_date,
            round(gold_inr, 2),
            round(silver_inr, 2)
        )

conn.commit()
conn.close()

print("Full historical data loaded successfully!")
