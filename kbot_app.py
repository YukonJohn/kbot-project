import streamlit as st
import yfinance as yf
import pandas as pd
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

# ====================== TABS ======================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Analyzer", 
    "🚀 Market Trends", 
    "🌍 Global Pulse", 
    "⛏️ Gold & Mining Scanner",
    "📈 ETF Scanner",
    "📁 My Portfolio"
])

# ==========================================
# TAB 1-3: Your original tabs (kept simple)
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
                        fig = go.Figure(data=[go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'])])
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

with tab2:
    if st.button("Scan Trends"):
        try:
            resp = client.models.generate_content(model='gemini-2.5-flash-lite', contents="3 safe growth sectors for Kevin in 2026.")
            st.write(resp.text)
        except:
            st.info("AI is resting. Try again in 60 seconds.")

with tab3:
    if st.button("Check Global"):
        try:
            resp = client.models.generate_content(model='gemini-2.5-flash-lite', contents="Explain 2026 interest rates to Kevin.")
            st.write(resp.text)
        except:
            st.info("AI is resting. Try again in 60 seconds.")

# ==========================================
# TAB 4: GOLD & MINING SCANNER (Smarter Scoring)
# ==========================================
with tab4:
    st.subheader("⛏️ Gold, Silver & Mining Scanner")
    st.caption("Smart scoring: EMA + Volume + Relative Strength")

    mining_tickers = ["GOLD", "NEM", "AEM", "WPM", "FNV", "GFI", "AU", "KGC", "PAAS", "AG", "HL", "CDE", "EXK", "MAG", "SIL", "GDX", "GDXJ", "SILJ", "GLD", "SLV", "BTG", "EGO", "OR", "NG", "IAU", "PHYS"]

    if st.button("🚀 Start Gold & Mining Scanner"):
        placeholder = st.empty()
        while True:
            with placeholder.container():
                st.write(f"**Last refreshed:** {datetime.now().strftime('%H:%M:%S')}")
                results = []
                try:
                    gdx = yf.Ticker("GDX").history(period="5d", interval="5m")
                    gdx_change = ((gdx['Close'].iloc[-1] - gdx['Close'].iloc[-6]) / gdx['Close'].iloc[-6]) * 100 if len(gdx) > 5 else 0
                except:
                    gdx_change = 0

                for ticker in mining_tickers:
                    try:
                        hist = yf.Ticker(ticker).history(period="5d", interval="5m")
                        if len(hist) < 20: continue
                        price = hist['Close'].iloc[-1]
                        change = ((price - hist['Close'].iloc[-6]) / hist['Close'].iloc[-6]) * 100
                        ema20 = hist['Close'].ewm(span=20).mean().iloc[-1]
                        vol_surge = hist['Volume'].iloc[-1] > hist['Volume'].rolling(20).mean().iloc[-1] * 1.8
                        rel_strength = change - gdx_change

                        score = 0
                        if price > ema20: score += 35
                        if vol_surge: score += 30
                        if rel_strength > 0: score += 25
                        if change > 1.0: score += 10

                        results.append({"Ticker": ticker, "Price": round(price,4), "Change %": round(change,2), "Rel vs GDX": round(rel_strength,2), "Score": int(score)})
                    except:
                        continue

                if results:
                    df = pd.DataFrame(results).sort_values("Score", ascending=False)
                    st.dataframe(df, use_container_width=True, height=650)
                    st.success(f"**Top Picks:** {', '.join(df.head(5)['Ticker'].tolist())}")
            time.sleep(60)

# ==========================================
# TAB 5: ETF SCANNER (Smarter Scoring)
# ==========================================
with tab5:
    st.subheader("📈 ETF Scanner")
    st.caption("Smart scoring for ETFs")

    etf_tickers = ["GLD","SLV","GDX","GDXJ","SILJ","IAU","PHYS","SPY","QQQ","IWM","VTI","VOO","VUG","VTV","XLK","XLF","XLE","XLV","XLI","XLU"]

    if st.button("🚀 Start ETF Scanner"):
        placeholder = st.empty()
        while True:
            with placeholder.container():
                st.write(f"**Last refreshed:** {datetime.now().strftime('%H:%M:%S')}")
                results = []
                for ticker in etf_tickers:
                    try:
                        hist = yf.Ticker(ticker).history(period="5d", interval="5m")
                        if len(hist) < 15: continue
                        price = hist['Close'].iloc[-1]
                        change = ((price - hist['Close'].iloc[-6]) / hist['Close'].iloc[-6]) * 100
                        ema20 = hist['Close'].ewm(span=20).mean().iloc[-1]
                        vol_surge = hist['Volume'].iloc[-1] > hist['Volume'].rolling(20).mean().iloc[-1] * 1.5

                        score = 0
                        if price > ema20: score += 40
                        if vol_surge: score += 25
                        if change > 0.5: score += 25
                        if change > 1.5: score += 10

                        results.append({"Ticker": ticker, "Price": round(price,4), "Change %": round(change,2), "Score": int(score)})
                    except:
                        continue

                if results:
                    df = pd.DataFrame(results).sort_values("Score", ascending=False)
                    st.dataframe(df, use_container_width=True, height=650)
                    st.success(f"**Top ETFs:** {', '.join(df.head(6)['Ticker'].tolist())}")
            time.sleep(60)

# ==========================================
# TAB 6: MY PORTFOLIO
# ==========================================
with tab6:
    st.subheader("📁 My Personal Portfolio")

    if "my_portfolio" not in st.session_state:
        st.session_state.my_portfolio = []

    new_ticker = st.text_input("Add Ticker to Portfolio (e.g. GOLD, GDX, SPY):")
    if st.button("Add to Portfolio"):
        if new_ticker.strip().upper() not in st.session_state.my_portfolio:
            st.session_state.my_portfolio.append(new_ticker.strip().upper())
            st.success(f"Added {new_ticker.upper()}")
        else:
            st.warning("Already in portfolio")

    if st.button("Clear Portfolio"):
        st.session_state.my_portfolio = []
        st.success("Portfolio cleared")

    if st.session_state.my_portfolio:
        if st.button("Monitor My Portfolio"):
            placeholder = st.empty()
            while True:
                with placeholder.container():
                    st.write(f"**Last refreshed:** {datetime.now().strftime('%H:%M:%S')}")
                    results = []
                    for ticker in st.session_state.my_portfolio:
                        try:
                            hist = yf.Ticker(ticker).history(period="3d", interval="5m")
                            if len(hist) < 10: continue
                            price = hist['Close'].iloc[-1]
                            change = ((price - hist['Close'].iloc[-6]) / hist['Close'].iloc[-6]) * 100
                            ema20 = hist['Close'].ewm(span=20).mean().iloc[-1]
                            score = 40 if price > ema20 else 0
                            results.append({"Ticker": ticker, "Price": round(price,4), "Change %": round(change,2), "Score": int(score)})
                        except:
                            continue
                    if results:
                        df = pd.DataFrame(results).sort_values("Score", ascending=False)
                        st.dataframe(df, use_container_width=True)
                time.sleep(60)
    else:
        st.info("Add some tickers to your portfolio above to start monitoring.")
