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
    # We use the newest stable model name for 2026
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Vault Error: GOOGLE_API_KEY not found.")
    st.stop()

st.set_page_config(page_title="Kbot Assistant", layout="wide") 
st.title("🤖 Kbot: The Ultimate Financial Assistant")
st.write("Welcome, Kevin!")

# --- 3. THE ANALYZER ---
ticker_input = st.text_input("Enter Ticker (e.g., AAPL, RY.TO):", "RY.TO")

if st.button("Analyze"):
    with st.spinner("Kbot is thinking..."):
        try:
            ticker = ticker_input.strip().upper()
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1y")
            
            if not hist.empty:
                price = round(hist['Close'].iloc[-1], 2)
                st.success(f"✅ Found live data for: {ticker} (${price})")
                
                # Draw the chart
                fig = go.Figure(data=[go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'])])
                fig.update_layout(template="plotly_dark", height=400)
                st.plotly_chart(fig, use_container_width=True)

                # 4. THE AI SUMMARY (Updated to Gemini 2.5)
                try:
                    prompt = f"You are Kbot. Kevin wants a 3-paragraph long-term analysis of {ticker} which is currently at ${price}."
                    resp = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
                    st.divider()
                    st.subheader("🧠 Kbot's Executive Summary")
                    st.write(resp.text)
                except Exception as e:
                    st.error(f"AI Snag: {e}")
            else:
                st.error("Could not find data for that ticker.")
        except Exception as e:
            st.error(f"Connection Error: {e}")