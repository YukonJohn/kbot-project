import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from google import genai

# --- THE VAULT CHECK ---
if "GOOGLE_API_KEY" not in st.secrets or "APP_PASSWORD" not in st.secrets:
    st.error("⚠️ Vault Error: Please check your Streamlit Secrets dashboard.")
    st.stop()

# Initialize the AI Client simply
client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])

# --- THE BOUNCER ---
password_guess = st.text_input("Enter the secret password to unlock Kbot:", type="password")
if password_guess != st.secrets["APP_PASSWORD"]:
    st.stop()

# --- KBOT'S INTERFACE ---
st.set_page_config(page_title="Kbot Assistant", layout="wide") 
st.title("🤖 Kbot: The Ultimate Financial Assistant")
st.write("Welcome, Kevin!")

tab1, tab2, tab3 = st.tabs(["📊 Analyzer", "🚀 Trends", "🌍 Global Pulse"])

# --- TAB 1: THE ANALYZER ---
with tab1:
    ticker = st.text_input("Enter a Ticker (e.g., AAPL, RY.TO):", "RY.TO").strip().upper()
    if st.button("Analyze"):
        with st.spinner("Kbot is digging for info..."):
            all_info = f"Ticker: {ticker}\n"
            data_found = False

            # Try to get market data
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="1y")
                if not hist.empty:
                    data_found = True
                    price = round(hist['Close'].iloc[-1], 2)
                    all_info += f"Market Data: Found. Current Price: ${price}\n"
                    st.success(f"📈 Found live data for {ticker} (${price})")
                    fig = go.Figure(data=[go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'])])
                    fig.update_layout(template="plotly_dark", height=400)
                    st.plotly_chart(fig, use_container_width=True)
            except:
                st.warning(f"⚠️ Yahoo is blocking the 'Cloud' connection for {ticker}. Kbot will use his internal memory instead.")

            # CALL THE AI (Kbot's Brain)
            try:
                prompt = f"You are Kbot. Kevin wants to know about {ticker}. "
                if data_found:
                    prompt += f"I found market data: {all_info}. Give a 3-paragraph long-term analysis."
                else:
                    prompt += "I couldn't get live market data, so use your own knowledge to give Kevin a general long-term outlook for this asset."
                
                # Using the stable 1.5-flash model for better web connection
                resp = client.models.generate_content(model='gemini-1.5-flash', contents=prompt)
                st.divider()
                st.subheader("🧠 Kbot's Executive Summary")
                st.write(resp.text)
            except Exception as e:
                st.error(f"❌ AI Snag: {e}")

# --- TAB 2 & 3: SIMPLIFIED ---
with tab2:
    if st.button("Scan Trends"):
        with st.spinner("Scanning..."):
            try:
                resp = client.models.generate_content(model='gemini-1.5-flash', contents="Kevin wants to know 3 strong sectors for long-term growth.")
                st.write(resp.text)
            except: st.error("AI connection lost.")

with tab3:
    if st.button("Check Global"):
        with st.spinner("Checking Bonds..."):
            try:
                resp = client.models.generate_content(model='gemini-1.5-flash', contents="Explain to Kevin how Yukon interest rates compare to the US national average for long-term investors.")
                st.write(resp.text)
            except: st.error("AI connection lost.")