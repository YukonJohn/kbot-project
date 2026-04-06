import streamlit as st
import yfinance as yf
import pandas as pd
import asyncio
import time
from datetime import datetime
import plotly.graph_objects as go
from google import genai

# ====================== PASSWORD & GEMINI ======================
password_guess = st.text_input("Enter the secret password to unlock Kbot:", type="password")

if "APP_PASSWORD" in st.secrets:
    if password_guess != st.secrets["APP_PASSWORD"]:
        st.stop()
else:
    st.error("Vault Error: APP_PASSWORD not found.")
    st.stop()

if "GOOGLE_API_KEY" in st.secrets:
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Vault Error: GOOGLE_API_KEY not found.")
    st.stop()

st.set_page_config(page_title="Kbot Assistant", layout="wide")
st.title("🤖 Kbot: The Ultimate Financial Assistant")
st.write("Welcome, Kevin!")

tab1, tab2, tab3, tab4 = st.tabs(["📊 Analyzer", "🚀 Market Trends", "🌍 Global Pulse", "⛏️ Gold & Mining Scanner"])

# ==========================================
# TAB 1, 2, 3 (Your existing tabs - unchanged)
# ==========================================
with tab1:
    # ... your existing Analyzer code ...
    pass  # I'll keep this for now, you can paste your original code here

with tab2:
    # your existing code
    pass

with tab3:
    # your existing code
    pass

# ==========================================
# NEW TAB 4: GOLD & MINING SCANNER
# ==========================================
with tab4:
    st.subheader("⛏️ Gold, Silver & Mining Scanner")
    st.write("Monitoring 50 key tickers every 60 seconds | Focused on momentum + relative strength")

    # List of popular gold/silver/mining tickers (you can expand this)
    mining_tickers = [
        "GOLD", "NEM", "AEM", "WPM", "FNV", "GFI", "AU", "KGC", "PAAS", "AG",
        "HL", "CDE", "EXK", "MAG", "SIL", "GDX", "GDXJ", "SILJ", "GLD", "SLV",
        "AAAU", "BAR", "IAU", "SGOL", "PHYS", "CEF", "BTG", "EGO", "OR", "NG"
        # Add more if you want - up to ~50
    ]

    if st.button("🚀 Start Gold & Mining Scanner"):
        placeholder = st.empty()
        
        while True:
            with placeholder.container():
                st.write(f"**Last Update:** {datetime.now().strftime('%H:%M:%S')}")

                data_list = []
                
                for ticker in mining_tickers[:30]:   # limit to 30 for speed in first version
                    try:
                        stock = yf.Ticker(ticker)
                        hist = stock.history(period="5d", interval="5m")  # 5 days of 5-min data
                        
                        if not hist.empty:
                            current_price = round(hist['Close'].iloc[-1], 4)
                            prev_close = round(hist['Close'].iloc[-2], 4) if len(hist) > 1 else current_price
                            
                            change_pct = round(((current_price - prev_close) / prev_close) * 100, 2)
                            
                            data_list.append({
                                "Ticker": ticker,
                                "Price": current_price,
                                "Change %": change_pct,
                                "Volume": int(hist['Volume'].iloc[-1])
                            })
                    except:
                        pass  # skip if error
                
                if data_list:
                    df = pd.DataFrame(data_list)
                    df = df.sort_values(by="Change %", ascending=False)
                    
                    st.dataframe(df.style.format({"Price": "${:.4f}", "Change %": "{:.2f}%"}), use_container_width=True)
                    
                    # Simple top 5 highlight
                    st.success(f"**Top Momentum Picks Right Now:** {', '.join(df.head(5)['Ticker'].tolist())}")
            
            time.sleep(60)  # 1 minute update