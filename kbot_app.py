import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime
import plotly.graph_objects as go
from google import genai
from streamlit_gsheets import GSheetsConnection

# ====================== PASSWORD & GEMINI SETUP ======================
st.set_page_config(page_title="Kbot Assistant", layout="wide")

password_guess = st.text_input("Enter the secret password to unlock Kbot:", type="password")
if "APP_PASSWORD" in st.secrets and password_guess != st.secrets["APP_PASSWORD"]:
    st.info("Please enter the password to proceed.")
    st.stop()

# Initialize Gemini Client
client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])

# ====================== CLOUD PORTFOLIO (GSHEETS) ======================
# The URL to your "Kbot_Data" sheet
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1qwvK233eN40Hz_tM_OC--ROK7SUFf8vttYDlW0wY398/edit#gid=0"

conn = st.connection("gsheets", type=GSheetsConnection)

def get_portfolio_from_sheets():
    try:
        # Looking at the 'Portfolio' tab in your Google Sheet
        df = conn.read(spreadsheet=SPREADSHEET_URL, worksheet="Portfolio", ttl=0)
        return df["Ticker"].dropna().tolist() if not df.empty else []
    except:
        return []

def save_to_sheets(ticker_list):
    try:
        df = pd.DataFrame({"Ticker": ticker_list})
        conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Portfolio", data=df)
    except Exception as e:
        st.error(f"Error saving to Cloud: {e}")

# Sync sheets to session state
if "my_portfolio" not in st.session_state:
    st.session_state.my_portfolio = get_portfolio_from_sheets()

# ====================== THE SCORING LOGIC ======================
def get_advanced_score(ticker, gdx_change=0):
    try:
        hist = yf.Ticker(ticker).history(period="5d", interval="5m")
        if len(hist) < 20: return None
        
        price = hist['Close'].iloc[-1]
        change = ((price - hist['Close'].iloc[-6]) / hist['Close'].iloc[-6]) * 100
        ema20 = hist['Close'].ewm(span=20).mean().iloc[-1]
        vol_surge = hist['Volume'].iloc[-1] > hist['Volume'].rolling(20).mean().iloc[-1] * 1.8
        rel_strength = change - gdx_change

        score = 0
        # BUY SIGNALS
        if price > ema20: score += 35
        if vol_surge: score += 30
        if rel_strength > 0.5: score += 25
        
        # SELL / WARNING SIGNALS
        if price < ema20: score -= 50  # Penalty for breaking trend
        if change < -1.5: score -= 20  # Sharp drop
        
        return {"Ticker": ticker, "Price": round(price, 4), "Score": int(score)}
    except:
        return None

# ====================== INTERFACE & TABS ======================
st.title("🤖 Kbot: The Ultimate Financial Assistant")

tabs = st.tabs([
    "📊 Analyzer", 
    "🚀 Trends", 
    "🌍 Global Pulse", 
    "⛏️ Mining Scanner", 
    "📁 My Portfolio", 
    "🏆 Top 10 Scanner"
])

# --- TAB 1 to 4: (Placeholders for your existing logic) ---
with tabs[0]: st.write("Analyzer Logic Goes Here")
with tabs[1]: st.write("Trends Logic Goes Here")
with tabs[2]: st.write("Global Pulse Logic Goes Here")
with tabs[3]: st.write("Mining Scanner Logic Goes Here")

# --- TAB 5: MY PORTFOLIO ---
with tabs[4]:
    st.header("📁 My Portfolio")
    new_ticker = st.text_input("Add Ticker to Portfolio (e.g., TSLA or SHOP.TO):").upper()
    if st.button("Add Ticker"):
        if new_ticker and new_ticker not in st.session_state.my_portfolio:
            st.session_state.my_portfolio.append(new_ticker)
            save_to_sheets(st.session_state.my_portfolio)
            st.success(f"Added {new_ticker}")

    st.write("### Current Holdings")
    st.write(st.session_state.my_portfolio)
    if st.button("Clear Portfolio"):
        st.session_state.my_portfolio = []
        save_to_sheets([])
        st.rerun()

# --- TAB 6: TOP 10 SCANNER (Kevin's Request) ---
with tabs[5]:
    st.header("🏆 Market Leaderboard")
    st.write("Ranking the best opportunities in US and Canadian markets.")

    col1, col2 = st.columns(2)
    
    # Pre-defined lists of major stocks
    us_tickers = ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "GOOGL", "META", "AMD", "NFLX", "INTC"]
    cnd_tickers = ["SHOP.TO", "TD.TO", "RY.TO", "ENB.TO", "CNR.TO", "CP.TO", "BN.TO", "TRI.TO", "BMO.TO", "ATD.TO"]

    with col1:
        if st.button("🚀 Scan US Market"):
            results = []
            bar = st.progress(0)
            for i, t in enumerate(us_tickers):
                res = get_advanced_score(t)
                if res: results.append(res)
                bar.progress((i + 1) / len(us_tickers))
            
            df_us = pd.DataFrame(results).sort_values(by="Score", ascending=False).head(10)
            st.table(df_us)

    with col2:
        if st.button("🍁 Scan CND Market"):
            results = []
            bar = st.progress(0)
            for i, t in enumerate(cnd_tickers):
                res = get_advanced_score(t)
                if res: results.append(res)
                bar.progress((i + 1) / len(cnd_tickers))
            
            df_cnd = pd.DataFrame(results).sort_values(by="Score", ascending=False).head(10)
            st.table(df_cnd)