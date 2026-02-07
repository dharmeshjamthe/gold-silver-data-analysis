import pyodbc
import yfinance as yf
from datetime import date

# ===== DB CONFIG =====
SERVER = r"localhost\SQLEXPRESS"
DB = "GoldSilverDB"
TABLE = "DailyPrices"

# ===== UNIT CONVERSIONS =====
TROY_OUNCE_TO_GRAM = 31.1034768
GOLD_10G_IN_TROY_OZ = 10 / TROY_OUNCE_TO_GRAM        # gold 10g
SILVER_1KG_IN_TROY_OZ = 1000 / TROY_OUNCE_TO_GRAM    # silver 1kg


def get_latest_close(ticker: str) -> tuple[float, str]:
    """
    Returns (close_price, close_date_str).
    Uses last few days so weekend/holiday pe bhi last available mil jaye.
    """
    df = yf.Ticker(ticker).history(period="7d")
    if df is None or df.empty:
        raise ValueError(f"No data for {ticker}")

    last_row = df.dropna().iloc[-1]
    close_price = float(last_row["Close"])
    close_date_str = df.dropna().index[-1].date().strftime("%Y-%m-%d")
    return close_price, close_date_str


def upsert_daily(conn, price_date, gold_10g_inr, silver_1kg_inr):
    cursor = conn.cursor()
    cursor.execute(f"""
        IF EXISTS (SELECT 1 FROM {TABLE} WHERE PriceDate = ?)
            UPDATE {TABLE}
            SET GoldPrice = ?, SilverPrice = ?
            WHERE PriceDate = ?
        ELSE
            INSERT INTO {TABLE} (PriceDate, GoldPrice, SilverPrice)
            VALUES (?, ?, ?)
    """, price_date, gold_10g_inr, silver_1kg_inr, price_date,
         price_date, gold_10g_inr, silver_1kg_inr)


def main():
    today = date.today()  # DB me record aaj ki date se jayega

    gold_usd_per_oz, gold_src_dt = get_latest_close("GC=F")
    silver_usd_per_oz, silver_src_dt = get_latest_close("SI=F")
    usd_inr, fx_src_dt = get_latest_close("USDINR=X")

    gold_10g_inr = round(gold_usd_per_oz * usd_inr * GOLD_10G_IN_TROY_OZ, 2)
    silver_1kg_inr = round(silver_usd_per_oz * usd_inr * SILVER_1KG_IN_TROY_OZ, 2)

    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        f"SERVER={SERVER};"
        f"DATABASE={DB};"
        "Trusted_Connection=yes;"
    )

    try:
        upsert_daily(conn, today, gold_10g_inr, silver_1kg_inr)
        conn.commit()
    finally:
        conn.close()

    print("Saved for date:", today.strftime("%Y-%m-%d"))
    print("Source dates -> Gold:", gold_src_dt, "Silver:", silver_src_dt, "USDINR:", fx_src_dt)
    print("USDINR:", usd_inr)
    print("Gold 10g INR:", gold_10g_inr)
    print("Silver 1kg INR:", silver_1kg_inr)


if __name__ == "__main__":
    main()
print("Data added/updated successfully!")