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
        with st.spinner("Kbot is thinking..."):
            ticker_list = [t.strip().upper() for t in ticker_input.split(',')]
            all_data = ""
            for sym in ticker_list:
                try:
                    stock = yf.Ticker(sym)
                    hist = stock.history(period="1y")
                    if not hist.empty:
                        last_price = round(hist['Close'].iloc[-1], 2)
                        all_data += f"Asset: {sym} | Current Price: {last_price}\n"
                        st.write(f"✅ Found data for: {sym} (${last_price})")
                        fig = go.Figure(data=[go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'])])
                        fig.update_layout(template="plotly_dark", height=300, margin=dict(l=0,r=0,t=30,b=0))
                        st.plotly_chart(fig, use_container_width=True)
                except:
                    st.warning(f"Could not reach Yahoo for {sym}.")

            if all_data:
                # FIXED MODEL NAME HERE
                try:
                    resp = client.models.generate_content(model='gemini-2.0-flash', contents=f"Kevin wants a quick 3-paragraph analysis of: {all_data}")
                    st.divider()
                    st.subheader("🧠 Kbot's Executive Summary")
                    st.write(resp.text)
                except Exception as e:
                    st.error("The AI is taking a nap. Try again in a moment.")
            else:
                st.error("No stock data found to analyze.")

with tab2:
    if st.button("Scan Trends"):
        st.info("Kbot is scanning the market...")
        try:
            resp = client.models.generate_content(model='gemini-2.0-flash', contents="Kevin wants to know 3 strong stock market sectors for long-term investing right now.")
            st.write(resp.text)
        except:
            st.error("AI connection lost.")

with tab3:
    if st.button("Check Global"):
        st.info("Checking the global pulse...")
        try:
            resp = client.models.generate_content(model='gemini-2.0-flash', contents="Explain to Kevin how inflation and interest rates affect his stock portfolio in simple terms.")
            st.write(resp.text)
        except:
            st.error("AI connection lost.")