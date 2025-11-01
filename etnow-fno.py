import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from gnews import GNews
from datetime import datetime, timedelta

st.set_page_config(page_title="ET Now F&O News", layout="wide")

st.title("📈 ET Now News for All F&O Stocks")

# --- STEP 1: Fetch F&O stock list from NSE ---
@st.cache_data
def get_fno_stocks():
    url = "https://www1.nseindia.com/content/fo/fo_underlyinglist.htm"
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table')
    if table:
        df = pd.read_html(str(table))[0]
        df.columns = df.columns.str.strip()
        return df['SYMBOL'].dropna().unique().tolist()
    else:
        return ["RELIANCE", "INFY", "TCS", "HDFCBANK", "ICICIBANK"]  # fallback list

fno_stocks = get_fno_stocks()
st.sidebar.header("Filters")
timeframe = st.sidebar.selectbox(
    "Select timeframe",
    ["1 Week", "1 Month", "3 Months", "6 Months"]
)

# --- STEP 2: Define date range based on timeframe ---
now = datetime.now()
if timeframe == "1 Week":
    from_date = now - timedelta(weeks=1)
elif timeframe == "1 Month":
    from_date = now - timedelta(days=30)
elif timeframe == "3 Months":
    from_date = now - timedelta(days=90)
else:
    from_date = now - timedelta(days=180)

# --- STEP 3: Fetch ET Now / ET Markets news via GNews ---
def fetch_news(stock, from_date):
    google_news = GNews(language='en', country='IN', max_results=3)
    query = f"{stock} site:etnownews.com OR site:economictimes.indiatimes.com"
    news = google_news.get_news(query)
    filtered = []
    for n in news:
        try:
            date_obj = datetime.strptime(n['published date'], "%a, %d %b %Y %H:%M:%S %Z")
            if date_obj >= from_date:
                filtered.append({
                    "Stock": stock,
                    "Title": n['title'],
                    "Publisher": n['publisher']['title'],
                    "Published Date": date_obj.strftime("%Y-%m-%d"),
                    "Link": n['url']
                })
        except:
            continue
    return filtered

# --- STEP 4: Fetch news for top 10 F&O stocks ---
st.info(f"Fetching latest ET Now / ET Markets news for top 10 F&O stocks ({timeframe})…")

sample_stocks = fno_stocks[:10]  # limit for speed
all_news = []
for stock in sample_stocks:
    stock_news = fetch_news(stock, from_date)
    all_news.extend(stock_news)

# --- STEP 5: Display ---
if all_news:
    df_news = pd.DataFrame(all_news)
    st.dataframe(df_news, use_container_width=True)
else:
    st.warning("No recent ET Now / ET Markets news found for the selected timeframe.")

st.caption("Data fetched using ET Now, ET Markets and Google News API.")
