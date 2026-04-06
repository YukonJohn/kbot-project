import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime
import plotly.graph_objects as go
from google import genai

# ====================== PASSWORD PROTECTION ======================
password_guess = st.text_input("Enter the secret password to unlock Kbot:", type="password")

if "APP_PASSWORD" in st.secrets:
    if password_guess != st.secrets["APP_PASSWORD"]:
        st.stop()
else:
    st.error("Vault Error: APP_PASSWORD not found.")
    st.stop()

# ====================== GEMINI CLIENT ======================
if "GOOGLE_API_KEY" in st.secrets:
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Vault Error: GOOGLE_API_KEY not found.")
    st.stop()

st.set_page_config(page_title="Kbot Assistant", layout="wide")
st.title("🤖 Kbot: The Ultimate Financial Assistant")
st.write("Welcome, Kevin!")

# ====================== TABS ======================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Analyzer", 
    "🚀 Market Trends", 
    "🌍 Global Pulse", 
    "⛏️ Gold & Mining Scanner",
    "📈 ETF Scanner"
])

# ==========================================
# TAB 1: ANALYZER (Your original)
# ==========================================
with tab1:
    ticker_input = st.text_input("Enter Tickers (e.g., AAPL, RY.TO, GOLD):", "RY.TO")

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
                        
                        fig = go.Figure(data=[go.Candlestick(
                            x=hist.index, 
                            open=hist['Open'], 
                            high=hist['High'], 
                            low=hist['Low'], 
                            close=hist['Close']
                        )])
                        fig.update_layout(template="plotly_dark", height=350)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning(f"⚠️ No data for {sym}")
                except Exception as e:
                    st.warning(f"⚠️ Error for {sym}: {e}")

            if all_summary_data:
                try:
                    prompt = f"Kevin wants a quick analysis of these tickers: {all_summary_data}"
                    resp = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
                    st.divider()
                    st.subheader("🧠 Kbot's Executive Summary")
                    st.write(resp.text)
                except Exception as e:
                    st.error(f"AI Error: {e}")

# ==========================================
# TAB 2: Market Trends
# ==========================================
with tab2:
    if st.button("Scan Trends"):
        try:
            resp = client.models.generate_content(model='gemini-2.5-flash-lite', contents="3 safe growth sectors for Kevin in 2026.")
            st.write(resp.text)
        except:
            st.info("AI is resting. Try again in 60 seconds.")

# ==========================================
# TAB 3: Global Pulse
# ==========================================
with tab3:
    if st.button("Check Global"):
        try:
            resp = client.models.generate_content(model='gemini-2.5-flash-lite', contents="Explain 2026 interest rates to Kevin.")
            st.write(resp.text)
        except:
            st.info("AI is resting. Try again in 60 seconds.")

# ==========================================
# TAB 4: GOLD & MINING SCANNER
# ==========================================
with tab4:
    st.subheader("⛏️ Gold, Silver & Mining Scanner")
    st.caption("Updates every 60 seconds • Momentum + Volume scoring")

    mining_tickers = [
        "GOLD", "NEM", "AEM", "WPM", "FNV", "GFI", "AU", "KGC", "PAAS", "AG",
        "HL", "CDE", "EXK", "MAG", "SIL", "GDX", "GDXJ", "SILJ", "GLD", "SLV",
        "BTG", "EGO", "OR", "NG", "IAU", "PHYS"
    ]

    if st.button("🚀 Start Gold & Mining Scanner"):
        placeholder = st.empty()
        
        while True:
            with placeholder.container():
                st.write(f"**Last refreshed:** {datetime.now().strftime('%H:%M:%S')}")

                results = []
                
                for ticker in mining_tickers:
                    try:
                        stock = yf.Ticker(ticker)
                        hist = stock.history(period="3d", interval="5m")
                        
                        if len(hist) < 10:
                            continue
                        
                        current_price = hist['Close'].iloc[-1]
                        prev_price = hist['Close'].iloc[-6] if len(hist) > 5 else current_price
                        change_pct = ((current_price - prev_price) / prev_price) * 100
                        
                        ema20 = hist['Close'].ewm(span=20).mean().iloc[-1]
                        avg_volume = hist['Volume'].rolling(20).mean().iloc[-1]
                        volume_surge = hist['Volume'].iloc[-1] > avg_volume * 1.8
                        
                        score = 0
                        if current_price > ema20: score += 45
                        if volume_surge: score += 35
                        if change_pct > 0: score += 20
                        
                        results.append({
                            "Ticker": ticker,
                            "Price": round(current_price, 4),
                            "Change %": round(change_pct, 2),
                            "Score": int(score),
                            "Volume Surge": "Yes" if volume_surge else "No"
                        })
                    except:
                        continue
                
                if results:
                    df = pd.DataFrame(results)
                    df = df.sort_values(by="Score", ascending=False).reset_index(drop=True)
                    
                    st.dataframe(df, use_container_width=True, height=650)
                    
                    top_picks = df.head(5)["Ticker"].tolist()
                    st.success(f"**Top 5 Right Now:** {', '.join(top_picks)}")
                else:
                    st.warning("Waiting for data...")

            time.sleep(60)

# ==========================================
# TAB 5: ETF SCANNER
# ==========================================
with tab5:
    st.subheader("📈 ETF Scanner")
    st.caption("Updates every 60 seconds • Strong ETFs including Gold & Silver")

    etf_tickers = [
        "GLD", "SLV", "GDX", "GDXJ", "SILJ", "IAU", "PHYS", "SGOL", "BAR", "AAAU",
        "SPY", "QQQ", "IWM", "VTI", "VOO", "VUG", "VTV", "XLK", "XLF", "XLE",
        "XLV", "XLI", "XLU", "XLRE", "XLY", "XLP", "XLC", "XLB", "XOP", "URA"
    ]

    if st.button("🚀 Start ETF Scanner"):
        placeholder = st.empty()
        
        while True:
            with placeholder.container():
                st.write(f"**Last refreshed:** {datetime.now().strftime('%H:%M:%S')}")

                results = []
                
                for ticker in etf_tickers:
                    try:
                        stock = yf.Ticker(ticker)
                        hist = stock.history(period="3d", interval="5m")
                        
                        if len(hist) < 15:
                            continue
                        
                        current_price = hist['Close'].iloc[-1]
                        prev_price = hist['Close'].iloc[-6] if len(hist) > 5 else current_price
                        change_pct = ((current_price - prev_price) / prev_price) * 100
                        
                        ema20 = hist['Close'].ewm(span=20).mean().iloc[-1]
                        volume_surge = hist['Volume'].iloc[-1] > hist['Volume'].rolling(20).mean().iloc[-1] * 1.5
                        
                        score = 0
                        if current_price > ema20: score += 40
                        if volume_surge: score += 25
                        if change_pct > 0.3: score += 25
                        if change_pct > 1.0: score += 10
                        
                        results.append({
                            "Ticker": ticker,
                            "Price": round(current_price, 4),
                            "Change %": round(change_pct, 2),
                            "Score": int(score),
                            "Volume Surge": "Yes" if volume_surge else "No"
                        })
                    except:
                        continue
                
                if results:
                    df = pd.DataFrame(results)
                    df = df.sort_values(by="Score", ascending=False).reset_index(drop=True)
                    
                    st.dataframe(df, use_container_width=True, height=700)
                    
                    top_picks = df.head(6)["Ticker"].tolist()
                    st.success(f"**Top 6 ETFs Right Now:** {', '.join(top_picks)}")
                else:
                    st.warning("Waiting for data...")

            time.sleep(60)