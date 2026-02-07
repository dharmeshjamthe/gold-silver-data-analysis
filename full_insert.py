import pyodbc
import yfinance as yf
from datetime import date

conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost\\SQLEXPRESS;"
    "DATABASE=GoldSilverDB;"
    "Trusted_Connection=yes;"
)
cursor = conn.cursor()

today = date.today()

gold = yf.Ticker("GC=F").history(period="1d")["Close"].iloc[-1]
silver = yf.Ticker("SI=F").history(period="1d")["Close"].iloc[-1]

cursor.execute(
    "INSERT INTO DailyPrices (PriceDate, GoldPrice, SilverPrice) VALUES (?, ?, ?)",
    today, float(gold), float(silver)
)

conn.commit()
conn.close()

print("Data added successfully!")
