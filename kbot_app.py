import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from google import genai
from google.genai import types # New tool for the timeout

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
    # We add a 120-second timeout here so it doesn't give up too early
    client = genai.Client(api_key=API_KEY, http_options={'timeout': 120000})
else:
    st.error("Vault Error: GOOGLE_API_KEY not found.")
    st.stop()

st.set_page_config(page_title="Kbot Assistant", layout="wide") 
st.title("🤖 Kbot: The Ultimate Financial Assistant")
st.write("Welcome, Kevin!")

tab1, tab2, tab3 = st.tabs(["📊 Analyzer", "🚀 Trends", "🌍 Global Pulse"])

with tab1:
    ticker_input = st.text_input("Enter Tickers (e.g., AAPL, RY.TO):", "RY.TO")
    if st.button("Analyze"):
        with st.spinner("Kbot is pulling the data..."):
            ticker_list = [t.strip().upper() for t in ticker_input.split(',')]
            all_data = ""
            for sym in ticker_list:
                try:
                    stock = yf.Ticker(sym)
                    hist = stock.history(period="1y")
                    if not hist.empty:
                        price = round(hist['Close'].iloc[-1], 2)
                        all_data += f"Asset: {sym} | Price: {price}\n"
                        st.write(f"✅ Found data for: {sym} (${price})")
                        fig = go.Figure(data=[go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'])])
                        fig.update_layout(template="plotly_dark", height=300)
                        st.plotly_chart(fig, use_container_width=True)
                except:
                    st.warning(f"Could not load {sym}")

            if all_data:
                try:
                    # We call the newest Gemini model here
                    resp = client.models.generate_content(
                        model='gemini-2.0-flash', 
                        contents=f"Kevin wants a quick analysis of: {all_data}"
                    )
                    st.divider()
                    st.subheader("🧠 Kbot's Executive Summary")
                    st.write(resp.text)
                except Exception as e:
                    # This now shows the REAL error instead of the "nap" message
                    st.error(f"The AI ran into a snag. Error details: {e}")
            else:
                st.error("No data found.")