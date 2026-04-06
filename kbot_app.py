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

# Create 4 tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Analyzer", "🚀 Market Trends", "🌍 Global Pulse", "⛏️ Gold & Mining Scanner"])

# ==========================================
# TAB 1: ANALYZER (Your original code)
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
# TAB 2 & 3 (Your original simple tabs)
# ==========================================
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
# NEW TAB 4: GOLD & MINING SCANNER
# ==========================================
with tab4:
    st.subheader("⛏️ Gold, Silver & Mining Scanner")
    st.caption("Updates every 60 seconds | Focused on momentum in mining sector")

    # You can expand this list later
    mining_tickers = [
        "GOLD", "NEM", "AEM", "WPM", "FNV", "GFI", "AU", "KGC", "PAAS", "AG",
        "HL", "CDE", "EXK", "MAG", "SIL", "GDX", "GDXJ", "SILJ", "GLD", "SLV",
        "BTG", "EGO", "OR", "NG", "IAU", "PHYS"
    ]

    if st.button("Start Scanner (1-minute updates)"):
        placeholder = st.empty()
        
        while True:
            with placeholder.container():
                st.write(f"**Last refreshed:** {datetime.now().strftime('%H:%M:%S')}")

                data_list = []
                
                for ticker in mining_tickers:
                    try:
                        stock = yf.Ticker(ticker)
                        # Get recent 5-minute data
                        hist = stock.history(period="2d", interval="5m")
                        
                        if not hist.empty:
                            current_price = round(hist['Close'].iloc[-1], 4)
                            prev_price = round(hist['Close'].iloc[-6], 4) if len(hist) > 5 else current_price
                            change_pct = round(((current_price - prev_price) / prev_price) * 100, 2)
                            volume = int(hist['Volume'].iloc[-1])

                            data_list.append({
                                "Ticker": ticker,
                                "Price": current_price,
                                "Change %": change_pct,
                                "Volume": volume
                            })
                    except:
                        continue  # skip if error

                if data_list:
                    df = pd.DataFrame(data_list)
                    df = df.sort_values(by="Change %", ascending=False).reset_index(drop=True)
                    
                    st.dataframe(
                        df.style.format({"Price": "${:.4f}", "Change %": "{:.2f}%"}),
                        use_container_width=True,
                        height=600
                    )
                    
                    top5 = df.head(5)["Ticker"].tolist()
                    st.success(f"**Current Top Momentum Picks:** {', '.join(top5)}")
                else:
                    st.warning("No data received. Trying again in 60 seconds...")

            time.sleep(60)   # Wait 1 minute before next update