import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from gnews import GNews
from datetime import datetime, timedelta
from dateutil.parser import parse as dateparse
import traceback
import time

st.set_page_config(page_title="ET Now / ET Markets F&O News", layout="wide")
st.title("📈 ET Now / ET Markets News for F&O Stocks (debuggable)")

# ----------------- Settings -----------------
st.sidebar.header("Settings")
sample_limit = st.sidebar.number_input("Stocks to fetch (set 0 for all from NSE list, but may be slow)", min_value=0, max_value=500, value=10)
max_results_per_stock = st.sidebar.slider("Max headlines per stock", 1, 10, 3)

timeframe = st.sidebar.selectbox("Select timeframe", ["1 Week", "1 Month", "3 Months", "6 Months"])
st.sidebar.markdown("If the NSE site blocks requests, the app will use a fallback sample list.")

# ----------------- Date range -----------------
now = datetime.now()
if timeframe == "1 Week":
    from_date = now - timedelta(weeks=1)
elif timeframe == "1 Month":
    from_date = now - timedelta(days=30)
elif timeframe == "3 Months":
    from_date = now - timedelta(days=90)
else:
    from_date = now - timedelta(days=180)

st.sidebar.write("Showing news from:", from_date.date(), "to", now.date())

# ----------------- Helper: fetch F&O stock list from NSE -----------------
@st.cache_data(ttl=3600)
def get_fno_stocks():
    # Common NSE F&O underlying list URL (may block automated requests)
    urls = [
        "https://www1.nseindia.com/content/fo/fo_underlyinglist.htm",
        "https://www.nseindia.com/content/fo/fo_underlyinglist.htm"
    ]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "en-US,en;q=0.9"
    }
    for url in urls:
        try:
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200 and "Symbol" in r.text:
                soup = BeautifulSoup(r.text, "html.parser")
                table = soup.find("table")
                if table:
                    df = pd.read_html(str(table))[0]
                    if "SYMBOL" in df.columns.str.upper().tolist():
                        # Normalize column names
                        df.columns = [c.strip().upper() for c in df.columns]
                        if "SYMBOL" in df.columns:
                            symbols = df["SYMBOL"].dropna().astype(str).str.strip().tolist()
                            return symbols
            # else try next url
        except Exception as e:
            # continue to next url
            continue

    # fallback list (common F&O names) if NSE fetch fails
    fallback = [
        "RELIANCE","TCS","INFY","HDFCBANK","ICICIBANK","HDFC","KOTAKBANK",
        "LT","SBIN","AXISBANK","ITC","BAJAJ-AUTO","BHARTIARTL","ASIANPAINT",
        "SUNPHARMA","BAJFINANCE","HINDUNILVR","MARUTI","UPL","POWERGRID"
    ]
    return fallback

# ----------------- Helper: fetch news for a stock -----------------
def fetch_news_for_stock(stock, from_date, max_results=3):
    results = []
    try:
        gnews = GNews(language='en', country='IN', max_results=max_results)
        # prioritize ET Now / ET Markets / Economic Times
        query = f'{stock} (site:etnownews.com OR site:etmarkets.in OR site:economictimes.indiatimes.com OR "ET Now" OR "ETMarkets")'
        items = gnews.get_news(query)
    except Exception as e:
        # If gnews fails, return with error message stored
        return [{"stock": stock, "error": f"gnews error: {e}"}]

    for it in ite
