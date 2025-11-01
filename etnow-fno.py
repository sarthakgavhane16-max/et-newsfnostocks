import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from gnews import GNews
from datetime import datetime, timedelta
from dateutil.parser import parse as dateparse

st.set_page_config(page_title="ET Now / ET Markets F&O News", layout="wide")
st.title("📈 ET Now / ET Markets News for F&O Stocks")

# ---------------- Fetch F&O stocks ----------------
@st.cache_data(ttl=3600)
def get_fno_stocks():
    try:
        url = "https://www1.nseindia.com/content/fo/fo_underlyinglist.htm"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find("table")
        df = pd.read_html(str(table))[0]
        if "SYMBOL" in df.columns:
            return df["SYMBOL"].dropna().unique().tolist()
    except Exception:
        pass

    # fallback if NSE blocks request
    return ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "ITC", "LT", "HDFC", "AXISBANK"]

# ---------------- Sidebar options ----------------
timeframe = st.sidebar.selectbox("Select Timeframe", ["1 Week", "1 Month", "3 Months", "6 Months"])
limit = st.sidebar.slider("Number of stocks to check", 5, 50, 10)

# Date range
now = datetime.now()
days = {"1 Week": 7, "1 Month": 30, "3 Months": 90, "6 Months": 180}[timeframe]
from_date = now - timedelta(days=days)

# ---------------- Fetch News ----------------
def fetch_news(stock, from_date):
    google_news = GNews(language="en", country="IN", max_results=3)
    query = f"{stock} site:etnownews.com OR site:etmarkets.com OR site:economictimes.indiatimes.com"
    news_items = google_news.get_news(query)

    data = []
    for item in news_items:
        title = item.get("title", "")
        link = item.get("url", "")
        publisher = item.get("publisher", {}).get("title", "")
        pub_date = item.get("published date", "")

        try:
            dt = dateparse(pub_date)
        except Exception:
            continue

        if dt >= from_date:
            data.append({
                "Stock": stock,
                "Title": title,
                "Publisher": publisher,
                "Published Date": dt.strftime("%Y-%m-%d"),
                "Link": link
            })
    return data

# ---------------- Run ----------------
stocks = get_fno_stocks()[:limit]
all_news = []
progress = st.progress(0)

for i, stock in enumerate(stocks):
    news = fetch_news(stock, from_date)
    all_news.extend(news)
    progress.progress((i + 1) / len(stocks))

if all_news:
    df = pd.DataFrame(all_news)
    st.dataframe(df, use_container_width=True)
    st.download_button("Download CSV", df.to_csv(index=False), "fno_news.csv")
else:
    st.warning("No recent ET Now / ET Markets news found.")

st.caption("Data from ET Now / ET Markets via Google News API")
