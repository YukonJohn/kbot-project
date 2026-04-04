import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from google import genai

# --- THE BOUNCER ---
password_guess = st.text_input("Enter the secret password to unlock Kbot:", type="password")

if "APP_PASSWORD" in st.secrets:
    if password_guess != st.secrets["APP_PASSWORD"]:
        st.stop()
else:
    st.error("Vault Error: APP_PASSWORD not found.")
    st.stop()

# --- THE VAULT KEY ---
if "GOOGLE_API_KEY" in st.secrets:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    client = genai.Client(api_key=API_KEY)
else:
    st.error("Vault Error: GOOGLE_API_KEY not found.")
    st.stop()

# --- KBOT'S FACE & TABS ---
st.set_page_config(page_title="Kbot Assistant", page_icon="📈", layout="wide") 
st.title("🤖 Kbot: The Ultimate Financial Assistant")
st.write("Welcome, Kevin!")

tab1, tab2, tab3 = st.tabs(["📊 Analyzer", "🚀 Trends", "🌍 Global Pulse"])

with tab1:
    ticker_input = st.text_input("Enter Tickers (e.g., AAPL, RY.TO):", "RY.TO")
    if st.button("Analyze"):
        with st.spinner("Analyzing..."):
            ticker_list = [t.strip().upper() for t in ticker_input.split(',')]
            all_data = ""
            for sym in ticker_list:
                stock = yf.Ticker(sym) # CLEANED: No session needed
                try:
                    info = stock.info
                    name = info.get('longName', sym)
                    all_data += f"Asset: {name}\nNews:\n"
                    for n in stock.news[:3]: all_data += f"- {n['title']}\n"
                    st.write(f"**{name} ({sym})**")
                    hist = stock.history(period="1y")
                    fig = go.Figure(data=[go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'])])
                    fig.update_layout(template="plotly_dark", height=300)
                    st.plotly_chart(fig, use_container_width=True)
                except: st.warning(f"Could not load {sym}")
            resp = client.models.generate_content(model='gemini-2.0-flash', contents=f"Analyze for Kevin: {all_data}")
            st.write(resp.text)

with tab2:
    if st.button("Scan Trends"):
        with st.spinner("Scanning..."):
            sectors = {"Tech": "XLK", "Health": "XLV", "Energy": "XLE"}
            txt = ""
            for n, t in sectors.items():
                s = yf.Ticker(t) # CLEANED: No session needed
                txt += f"Sector: {n}\nNews:\n"
                for art in s.news[:2]: txt += f"- {art['title']}\n"
            resp = client.models.generate_content(model='gemini-2.0-flash', contents=f"Pick a winner for Kevin: {txt}")
            st.write(resp.text)

with tab3:
    if st.button("Check Global"):
        with st.spinner("Checking..."):
            syms = {"10Y Bond": "^TNX", "USD/CAD": "CAD=X"}
            macro = ""
            for n, s in syms.items():
                d = yf.Ticker(s) # CLEANED: No session needed
                rate = d.history(period="1d")['Close'].iloc[-1]
                st.write(f"**{n}:** {round(rate, 3)}")
                macro += f"{n}: {rate}\n"
            resp = client.models.generate_content(model='gemini-2.0-flash', contents=f"Explain to Kevin: {macro}")
            st.write(resp.text)