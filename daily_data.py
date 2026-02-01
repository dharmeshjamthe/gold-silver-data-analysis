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

cursor.execute("SELECT COUNT(*) FROM DailyPrices WHERE PriceDate = ?", today)
if cursor.fetchone()[0] > 0:
    print("Today's data already exists")
    exit()

gold_df = yf.download("GC=F", period="10d")
silver_df = yf.download("SI=F", period="10d")

if gold_df.empty or silver_df.empty:
    print("Market closed or no data today")
    exit()

gold_price = float(gold_df["Close"].iloc[-1])
silver_price = float(silver_df["Close"].iloc[-1])

cursor.execute(
    "INSERT INTO DailyPrices VALUES (?, ?, ?)",
    today, gold_price, silver_price
)

conn.commit()
conn.close()

print("Data added successfully")
