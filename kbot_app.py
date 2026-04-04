import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from google import genai
import requests

# --- THE BOUNCER ---
# This looks for "APP_PASSWORD" in your Streamlit Secrets vault
password_guess = st.text_input("Enter the secret password to unlock Kbot:", type="password")

if "APP_PASSWORD" in st.secrets:
    if password_guess != st.secrets["APP_PASSWORD"]:
        st.warning("Please enter the correct password.")
        st.stop()
else:
    st.error("Vault Error: APP_PASSWORD not found in Streamlit Secrets.")
    st.stop()

# --- THE VAULT KEY ---
# This looks for "GOOGLE_API_KEY" in your Streamlit Secrets vault
if "GOOGLE_API_KEY" in st.secrets:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    client = genai.Client(api_key=API_KEY)
else:
    st.error("Vault Error: GOOGLE_API_KEY not found in Streamlit Secrets.")
    st.stop()

# --- THE DISGUISE (Fixes the Yahoo Rate Limit Error) ---
safe_session = requests.Session()
safe_session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/115.0.0.0 Safari/537.36'
})

# --- KBOT'S FACE & TABS ---
st.set_page_config(page_title="Kbot Assistant", page_icon="📈", layout="wide") 
st.title("🤖 Kbot: The Ultimate Financial Assistant")
st.write("Welcome, Kevin!")

tab1, tab2, tab3 = st.tabs(["📊 Analyzer (Stocks & ETFs)", "🚀 Market Trends", "🌍 Global Pulse (Bonds & Forex)"])

# --- TAB 1: ANALYZER ---
with tab1:
    st.subheader("Head-to-Head Analyzer")
    ticker_input = st.text_input("Enter Tickers (Add .TO for Canada! e.g., AAPL, RY.TO, SPY):", "RY.TO")

    if st.button("Analyze with Kbot"):
        with st.spinner("Kbot is analyzing..."):
            ticker_list = [ticker.strip().upper() for ticker in ticker_input.split(',')]
            all_data = ""
            for symbol in ticker_list:
                stock = yf.Ticker(symbol, session=safe_session)
                try:
                    info = stock.info
                    name = info.get('longName', symbol)
                    price = info.get('currentPrice', 'Price Hidden')
                    all_data += f"Asset: {name} ({symbol})\nNews:\n"
                    for n in stock.news[:3]: all_data += f"- {n['title']}\n"
                    st.write(f"**{name} ({symbol}):** ${price}")
                    hist = stock.history(period="1y")
                    fig = go.Figure(data=[go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'])])
                    fig.update_layout(template="plotly_dark", height=300)
                    st.plotly_chart(fig, use_container_width=True)
                except: st.warning(f"Could not load {symbol}")

            response = client.models.generate_content(model='gemini-2.0-flash', contents=f"User is Kevin. Analyze these assets for long-term: {all_data}")
            st.subheader("🧠 Kbot's Summary")
            st.write(response.text)

# --- TAB 2: TRENDS ---
with tab2:
    if st.button("Scan Market Trends"):
        with st.spinner("Scanning sectors..."):
            sectors = {"Tech": "XLK", "Health": "XLV", "Finance": "XLF", "Energy": "XLE"}
            sector_txt = ""
            for n, t in sectors.items():
                s = yf.Ticker(t, session=safe_session)
                sector_txt += f"Sector: {n}\nNews:\n"
                for art in s.news[:2]: sector_txt += f"- {art['title']}\n"
            resp = client.models.generate_content(model='gemini-2.0-flash', contents=f"Summarize these sectors for Kevin and pick a long-term winner: {sector_txt}")
            st.write(resp.text)

# --- TAB 3: GLOBAL ---
with tab3:
    if st.button("Check Global Pulse"):
        with st.spinner("Checking Bonds/Forex..."):
            symbols = {"10Y Bond": "^TNX", "EUR/USD": "EURUSD=X", "USD/CAD": "CAD=X"}
            macro_txt = ""
            for n, s in symbols.items():
                d = yf.Ticker(s, session=safe_session)
                rate = d.history(period="1d")['Close'].iloc[-1]
                st.write(f"**{n}:** {round(rate, 3)}")
                macro_txt += f"{n}: {rate}\n"
            resp = client.models.generate_content(model='gemini-2.0-flash', contents=f"Explain these rates to Kevin simply: {macro_txt}")
            st.write(resp.text)