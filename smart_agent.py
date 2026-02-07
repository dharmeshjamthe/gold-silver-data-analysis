import pandas as pd
import pyodbc
import numpy as np
from datetime import date

conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost\\SQLEXPRESS;"
    "DATABASE=GoldSilverDB;"
    "Trusted_Connection=yes;"
)

df = pd.read_sql("SELECT * FROM dbo.DailyPrices ORDER BY PriceDate", conn)

print("Rows loaded:", len(df))

prices = df["GoldPrice"].astype(float).values

# --- models ---
trend = np.polyfit(range(len(prices)), prices, 1)[0]
trend_signal = 1 if trend > 0 else -1

short_ma = pd.Series(prices).rolling(3).mean().iloc[-1]
long_ma = pd.Series(prices).rolling(7).mean().iloc[-1]
ma_signal = 1 if short_ma > long_ma else -1

momentum_signal = 1 if prices[-1] > prices[-3] else -1

signals = [trend_signal, ma_signal, momentum_signal]

score = sum(signals)
confidence = abs(score)/3*100

direction = "UP" if score > 0 else "DOWN"

mood = "Bullish" if confidence > 70 and direction=="UP" else \
       "Bearish" if confidence > 70 else "Neutral"

print("Prediction:", direction)
print("Confidence:", round(confidence,2))
print("Mood:", mood)

cursor = conn.cursor()
cursor.execute(
    "INSERT INTO PricePrediction VALUES (?, ?, ?, ?, ?)",
    date.today(), "Gold", direction, round(confidence,2), mood
)

conn.commit()
conn.close()
