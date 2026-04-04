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
    # Using the stable 2026 model name
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Vault Error: GOOGLE_API_KEY not found.")
    st.stop()

# --- 3. KBOT'S FACE & THE TABS ---
st.set_page_config(page_title="Kbot Assistant", layout="wide") 
st.title("🤖 Kbot: The Ultimate Financial Assistant")
st.write("Welcome, Kevin!")

# RESTORING YOUR TABS
tab1, tab2, tab3 = st.tabs(["📊 Analyzer", "🚀 Market Trends", "🌍 Global Pulse"])

# ==========================================
# TAB 1: THE ANALYZER (Multiple Stocks)
# ==========================================
with tab1:
    st.subheader("Head-to-Head Analyzer")
    # You can now enter multiple tickers again (e.g., AAPL, RY.TO, TD.TO)
    ticker_input = st.text_input("Enter Tickers (separated by commas):", "RY.TO, TD.TO")

    if st.button("Analyze with Kbot"):
        with st.spinner("Kbot is pulling the records..."):
            ticker_list = [t.strip().upper() for t in ticker_input.split(',')]
            all_summary_data = ""

            for sym in ticker_list:
                try:
                    stock = yf.Ticker(sym)
                    hist = stock.history(period="1y")
                    
                    if not hist.empty:
                        price = round(hist['Close'].iloc[-1], 2)
                        st.success(f"✅ Found: {sym} at ${price}")
                        
                        # Add to the data Kbot will read later
                        all_summary_data += f"Stock: {sym} | Current Price: ${price}\n"

                        # Draw the chart for this specific stock
                        fig = go.Figure(data=[go.Candlestick(
                            x=hist.index, open=hist['Open'], high=hist['High'], 
                            low=hist['Low'], close=hist['Close']
                        )])
                        fig.update_layout(title=f"1-Year Trend: {sym}", template="plotly_dark", height=350)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning(f"Could not find live data for {sym}.")
                except:
                    st.warning(f"Yahoo Finance connection failed for {sym}.")

            # If we found any data, Kbot writes one big summary for all of them
            if all_summary_data:
                try:
                    prompt = f"You are Kbot. Kevin wants a comparison and long-term outlook for these assets: {all_summary_data}. Identify which is the safer long-term hold."
                    resp = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
                    st.divider()
                    st.subheader("🧠 Kbot's Executive Summary")
                    st.write(resp.text)
                except Exception as e:
                    st.error(f"AI Snag: {e}")

# ==========================================
# TAB 2: RESTORING MARKET TRENDS
# ==========================================
with tab2:
    st.subheader("🚀 Global Market Trends")
    st.write("Kbot will scan the horizon for the best growth opportunities in 2026.")
    if st.button("Generate Trend Report"):
        with st.spinner("Scanning the horizon..."):
            try:
                prompt = "Give Kevin a report on the 3 strongest market sectors for long-term growth right now. Mention AI, Energy, and Healthcare."
                resp = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
                st.write(resp.text)
            except:
                st.error("AI connection lost. Try again in a minute.")

# ==========================================
# TAB 3: RESTORING GLOBAL PULSE
# ==========================================
with tab3:
    st.subheader("🌍 Global Pulse & Macro")
    st.write("Check how interest rates and the economy affect Kevin's portfolio.")
    if st.button("Check Global Health"):
        with st.spinner("Checking interest rates..."):
            try:
                prompt = "Explain to Kevin in 2 simple paragraphs how the current 2026 interest rates in Canada and the US affect his long-term stock holdings."
                resp = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
                st.write(resp.text)
            except:
                st.error("AI connection lost.")