import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from google import genai

# --- 1. THE BOUNCER ---
password_guess = st.text_input("Enter the secret password to unlock Kbot:", type="password")

if "APP_PASSWORD" in st.secrets:
    if password_guess != st.secrets["APP_PASSWORD"]:
        st.stop()
else:
    st.error("Vault Error: APP_PASSWORD not found.")
    st.stop()

# --- 2. THE VAULT KEY ---
if "GOOGLE_API_KEY" in st.secrets:
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Vault Error: GOOGLE_API_KEY not found.")
    st.stop()

st.set_page_config(page_title="Kbot Assistant", layout="wide") 
st.title("🤖 Kbot: The Ultimate Financial Assistant")
st.write("Welcome, Kevin!")

tab1, tab2, tab3 = st.tabs(["📊 Analyzer", "🚀 Market Trends", "🌍 Global Pulse"])

# ==========================================
# TAB 1: THE ANALYZER (Multiple Stocks)
# ==========================================
with tab1:
    ticker_input = st.text_input("Enter Tickers (e.g., AAPL, RY.TO):", "RY.TO")

    if st.button("Analyze with Kbot"):
        with st.spinner("Kbot is pulling the data..."):
            ticker_list = [t.strip().upper() for t in ticker_input.split(',')]
            all_summary_data = ""

            for sym in ticker_list:
                try:
                    stock = yf.Ticker(sym)
                    hist = stock.history(period="1y")
                    if not hist.empty:
                        price = round(hist['Close'].iloc[-1], 2)
                        all_summary_data += f"{sym}: ${price} | "
                        st.success(f"📈 {sym} Data Found: ${price}")
                        
                        fig = go.Figure(data=[go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'])])
                        fig.update_layout(template="plotly_dark", height=350)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning(f"⚠️ Yahoo is blocking the cloud for {sym}.")
                except:
                    st.warning(f"⚠️ Connection error for {sym}.")

            # THE AI SUMMARY (Now using 2026 stable models)
            if all_summary_data:
                try:
                    prompt = f"Kevin wants a quick analysis of: {all_summary_data}"
                    # TRY STABLE 2.5 FIRST
                    resp = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
                    st.divider()
                    st.subheader("🧠 Kbot's Executive Summary")
                    st.write(resp.text)
                except Exception as e:
                    if "429" in str(e):
                        st.info("🐢 **Rate Limit:** Retrying with Lite model...")
                        # AUTOMATIC FALLBACK TO LITE FOR SPEED
                        resp = client.models.generate_content(model='gemini-2.5-flash-lite', contents=prompt)
                        st.divider()
                        st.write(resp.text)
                    else:
                        st.error(f"AI Snag: {e}")

# ==========================================
# TABS 2 & 3 (AI ONLY)
# ==========================================
with tab2:
    if st.button("Scan Trends"):
        try:
            resp = client.models.generate_content(model='gemini-2.5-flash-lite', contents="3 safe growth sectors for Kevin in 2026.")
            st.write(resp.text)
        except: st.info("AI is resting. Try again in 60 seconds.")

with tab3:
    if st.button("Check Global"):
        try:
            resp = client.models.generate_content(model='gemini-2.5-flash-lite', contents="Explain 2026 interest rates to Kevin.")
            st.write(resp.text)
        except: st.info("AI is resting. Try again in 60 seconds.")