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

tab1, tab2, tab3 = st.tabs(["📊 Analyzer", "🚀 Trends", "🌍 Global Pulse"])

# ==========================================
# TAB 1: THE ANALYZER
# ==========================================
with tab1:
    ticker_input = st.text_input("Enter Tickers (e.g., AAPL, RY.TO):", "RY.TO")
    if st.button("Analyze"):
        with st.spinner("Kbot is pulling the records..."):
            tickers = [t.strip().upper() for t in ticker_input.split(',')]
            summary_data = ""
            for sym in tickers:
                try:
                    stock = yf.Ticker(sym)
                    hist = stock.history(period="1y")
                    if not hist.empty:
                        price = round(hist['Close'].iloc[-1], 2)
                        summary_data += f"{sym}: ${price} | "
                        st.success(f"📈 {sym} Data Found: ${price}")
                        fig = go.Figure(data=[go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'])])
                        fig.update_layout(template="plotly_dark", height=300)
                        st.plotly_chart(fig, use_container_width=True)
                except:
                    st.warning(f"Could not reach Yahoo for {sym}.")

            # CALL THE AI (With error handling so it doesn't crash the app)
            if summary_data:
                try:
                    # Using 1.5-flash as it is the most stable free model in 2026
                    resp = client.models.generate_content(model='gemini-1.5-flash', contents=f"Kevin needs a simple 2-paragraph long-term analysis of: {summary_data}")
                    st.divider()
                    st.subheader("🧠 Kbot's Executive Summary")
                    st.write(resp.text)
                except Exception as e:
                    if "429" in str(e):
                        st.info("💡 **Kbot is taking a breather.** The stock chart is above, but the AI summary is paused for 60 seconds due to Google's daily free limit.")
                    else:
                        st.error(f"AI Snag: {e}")

# ==========================================
# TABS 2 & 3 (AI ONLY)
# ==========================================
with tab2:
    if st.button("Scan Trends"):
        try:
            resp = client.models.generate_content(model='gemini-1.5-flash', contents="What are 3 safe sectors for Kevin to watch in 2026?")
            st.write(resp.text)
        except: st.info("AI is resting. Try again in a minute.")

with tab3:
    if st.button("Check Global"):
        try:
            resp = client.models.generate_content(model='gemini-1.5-flash', contents="Briefly explain how 2026 interest rates affect long-term stock portfolios.")
            st.write(resp.text)
        except: st.info("AI is resting. Try again in a minute.")