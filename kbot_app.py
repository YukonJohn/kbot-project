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
    st.error("Vault Error: APP_PASSWORD not found in Streamlit Secrets.")
    st.stop()

# --- 2. THE VAULT KEY ---
if "GOOGLE_API_KEY" in st.secrets:
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Vault Error: GOOGLE_API_KEY not found in Streamlit Secrets.")
    st.stop()

# --- 3. KBOT'S FACE & TABS ---
st.set_page_config(page_title="Kbot Assistant", layout="wide") 
st.title("🤖 Kbot: The Ultimate Financial Assistant")
st.write("Welcome, Kevin!")

tab1, tab2, tab3 = st.tabs(["📊 Analyzer", "🚀 Market Trends", "🌍 Global Pulse"])

# ==========================================
# TAB 1: THE ANALYZER (Multiple Stocks)
# ==========================================
with tab1:
    st.subheader("Head-to-Head Analyzer")
    ticker_input = st.text_input("Enter Tickers (separated by commas, e.g., AAPL, RY.TO):", "RY.TO")

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
                        all_summary_data += f"Stock: {sym} | Current Price: ${price}\n"
                        st.success(f"✅ Found data for {sym} (${price})")
                        
                        fig = go.Figure(data=[go.Candlestick(
                            x=hist.index, open=hist['Open'], high=hist['High'], 
                            low=hist['Low'], close=hist['Close']
                        )])
                        fig.update_layout(title=f"1-Year Trend: {sym}", template="plotly_dark", height=350)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning(f"⚠️ Yahoo is blocking the connection for {sym}. Kbot will use internal memory.")
                except:
                    st.warning(f"⚠️ Could not reach market for {sym}.")

            # THE AI SUMMARY WITH SAFETY VALVE
            try:
                # If no market data, Kbot uses general knowledge
                prompt_content = f"Analyze these assets for Kevin: {all_summary_data if all_summary_data else ticker_input}"
                resp = client.models.generate_content(model='gemini-2.0-flash', contents=prompt_content)
                st.divider()
                st.subheader("🧠 Kbot's Executive Summary")
                st.write(resp.text)
            except Exception as e:
                if "429" in str(e):
                    st.error("🐢 **Rate Limit:** Kbot is thinking too fast for the free version. Please wait 60 seconds and try again.")
                else:
                    st.error(f"AI Snag: {e}")

# ==========================================
# TAB 2: MARKET TRENDS
# ==========================================
with tab2:
    if st.button("Generate Trend Report"):
        with st.spinner("Scanning..."):
            try:
                resp = client.models.generate_content(model='gemini-2.0-flash', contents="Kevin wants to know 3 strong growth sectors for 2026.")
                st.write(resp.text)
            except Exception as e:
                st.error("AI is busy. Please wait a minute.")

# ==========================================
# TAB 3: GLOBAL PULSE
# ==========================================
with tab3:
    if st.button("Check Global Health"):
        with st.spinner("Checking rates..."):
            try:
                resp = client.models.generate_content(model='gemini-2.0-flash', contents="Explain to Kevin how 2026 interest rates affect his stock portfolio.")
                st.write(resp.text)
            except Exception as e:
                st.error("AI is busy. Please wait a minute.")