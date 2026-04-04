import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from google import genai

# --- THE BOUNCER ---
password_guess = st.text_input("Enter the secret password to unlock Kbot:", type="password")

if "APP_PASSWORD" in st.secrets:
    if password_guess != st.secrets["APP_PASSWORD"]:
        st.stop()
else:
    st.error("Vault Error: APP_PASSWORD not found.")
    st.stop()

# --- THE VAULT KEY ---
if "GOOGLE_API_KEY" in st.secrets:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    client = genai.Client(api_key=API_KEY)
else:
    st.error("Vault Error: GOOGLE_API_KEY not found.")
    st.stop()

# --- KBOT'S FACE & TABS ---
st.set_page_config(page_title="Kbot Assistant", page_icon="📈", layout="wide") 
st.title("🤖 Kbot: The Ultimate Financial Assistant")
st.write("Welcome, Kevin!")

tab1, tab2, tab3 = st.tabs(["📊 Analyzer", "🚀 Trends", "🌍 Global Pulse"])

with tab1:
    ticker_input = st.text_input("Enter Tickers (e.g., AAPL, RY.TO):", "RY.TO")
    if st.button("Analyze"):
        with st.spinner("Analyzing..."):
            ticker_list = [t.strip().upper() for t in ticker_input.split(',')]
            all_data = ""
            for sym in ticker_list:
                try:
                    stock = yf.Ticker(sym)
                    hist = stock.history(period="1y")
                    if not hist.empty:
                        name = sym # Using symbol as name for speed
                        all_data += f"Asset: {sym}\nLast Price: {hist['Close'].iloc[-1]}\n"
                        st.write(f"**Showing data for: {sym}**")
                        fig = go.Figure(data=[go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'])])
                        fig.update_layout(template="plotly_dark", height=300)
                        st.plotly_chart(fig, use_container_width=True)
                except:
                    st.warning(f"Yahoo Finance is busy. Could not load {sym} right now.")

            # SAFETY NET: Only call AI if we actually found data
            if all_data:
                resp = client.models.generate_content(model='gemini-1.5-flash', contents=f"Kevin wants a quick analysis of: {all_data}")
                st.write(resp.text)
            else:
                st.error("Kbot couldn't reach the stock market. Please wait a minute and try again.")

# --- THE OTHER TABS (SIMPLIFIED FOR STABILITY) ---
with tab2:
    if st.button("Scan Trends"):
        st.info("Scanning broad market sectors...")
        resp = client.models.generate_content(model='gemini-1.5-flash', contents="Kevin wants to know 3 strong stock market sectors for long-term investing.")
        st.write(resp.text)

with tab3:
    if st.button("Check Global"):
        st.info("Checking interest rates and bonds...")
        resp = client.models.generate_content(model='gemini-1.5-flash', contents="Explain to Kevin how high interest rates affect his stock portfolio in 2 paragraphs.")
        st.write(resp.text)