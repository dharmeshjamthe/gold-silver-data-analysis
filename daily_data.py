import pyodbc
import yfinance as yf
from datetime import date

# ---- SQL Connection ----
conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost\\SQLEXPRESS;"
    "DATABASE=GoldSilverDB;"
    "Trusted_Connection=yes;"
)
cursor = conn.cursor()

today = date.today()

# ---- Check if today's data already exists ----
cursor.execute(
    "SELECT COUNT(*) FROM DailyPrices WHERE PriceDate = ?", today
)

if cursor.fetchone()[0] > 0:
    print("Today's data already exists in database!")
    exit()

# ---- Fetch prices from Yahoo Finance ----
gold = yf.Ticker("GC=F").history(period="1d")["Close"].iloc[-1]
silver = yf.Ticker("SI=F").history(period="1d")["Close"].iloc[-1]

# ---- Insert into SQL ----
cursor.execute(
    "INSERT INTO DailyPrices (PriceDate, GoldPrice, SilverPrice) VALUES (?, ?, ?)",
    today, float(gold), float(silver)
)

conn.commit()
conn.close()

print("Today's gold & silver prices added successfully!")
