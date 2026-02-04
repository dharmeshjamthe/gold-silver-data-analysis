import pyodbc
import yfinance as yf
import requests
from datetime import date, timedelta
import time

# Configuration: adjust if needed
CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost\\SQLEXPRESS;"
    "DATABASE=GoldSilverDB;"
    "Trusted_Connection=yes;"
)

def get_usd_inr():
    try:
        fx = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=10).json()
        return fx["rates"]["INR"]
    except Exception as e:
        print("⚠ Could not fetch USD-INR rate:", e)
        return None

def main():
    conn = pyodbc.connect(CONN_STR)
    cursor = conn.cursor()

    start_date = date(date.today().year, 1, 1)
    end_date = date.today()

    usd_inr = get_usd_inr()
    if usd_inr is None:
        conn.close()
        return

    # Download historical data (end is exclusive in yfinance, so add one day)
    yf_start = start_date.isoformat()
    yf_end = (end_date + timedelta(days=1)).isoformat()

    print(f"Downloading gold ({yf_start} → {end_date.isoformat()})")
    gold_df = yf.download("GC=F", start=yf_start, end=yf_end, progress=False)
    print(f"Downloading silver ({yf_start} → {end_date.isoformat()})")
    silver_df = yf.download("SI=F", start=yf_start, end=yf_end, progress=False)

    gold_close = gold_df["Close"].dropna()
    silver_close = silver_df["Close"].dropna()

    # Normalize indices to date objects for easy lookup
    gold_map = {ts.date(): float(v) for ts, v in gold_close.items()}
    silver_map = {ts.date(): float(v) for ts, v in silver_close.items()}

    inserted = 0
    skipped_existing = 0
    skipped_missing = 0

    current = start_date
    batch = 0
    while current <= end_date:
        g = gold_map.get(current)
        s = silver_map.get(current)

        # require both prices to insert; change logic if you prefer partial rows
        if g is None or s is None:
            skipped_missing += 1
            current += timedelta(days=1)
            continue

        # Duplicate check
        cursor.execute("SELECT COUNT(*) FROM DailyPrices WHERE PriceDate = ?", current)
        if cursor.fetchone()[0] > 0:
            skipped_existing += 1
            current += timedelta(days=1)
            continue

        # Convert USD (per ounce) → INR for Indian market units
        gold_inr = g * usd_inr / 31.1 * 10
        silver_inr = s * usd_inr / 31.1 * 1000

        cursor.execute(
            "INSERT INTO DailyPrices (PriceDate, GoldPrice, SilverPrice) VALUES (?, ?, ?)",
            current,
            round(gold_inr, 2),
            round(silver_inr, 2),
        )
        inserted += 1
        batch += 1

        # Commit every 50 inserts to avoid long transactions
        if batch >= 50:
            conn.commit()
            batch = 0
            print(f"Committed {inserted} inserts so far...")

        # small sleep to be polite to services (optional)
        time.sleep(0.05)
        current += timedelta(days=1)

    if batch > 0:
        conn.commit()

    conn.close()

    print("Done.")
    print(f"Inserted: {inserted}")
    print(f"Skipped (existing): {skipped_existing}")
    print(f"Skipped (missing prices): {skipped_missing}")

if __name__ == "__main__":
    main()
