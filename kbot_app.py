import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from google import genai
import requests

# --- THE BOUNCER ---
password_guess = st.text_input("Enter the secret password to unlock Kbot:", type="password")

if password_guess != st.secrets["APP_PASSWORD"]:
    st.stop()

# --- THE VAULT KEY ---
API_KEY = st.secrets["GOOGLE_API_KEY"]
client = genai.Client(api_key=API_KEY)

# --- THE DISGUISE (Fixes the Yahoo Rate Limit Error) ---
safe_session = requests.Session()
safe_session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/115.0.0.0 Safari/537.36'
})

# --- KBOT'S FACE & TABS ---
st.set_page_config(page_title="Kbot Assistant", page_icon="📈", layout="wide") 
st.title("🤖 Kbot: The Ultimate Financial Assistant")
st.write("Welcome, Kevin!")

tab1, tab2, tab3 = st.tabs(["📊 Analyzer (Stocks & ETFs)", "🚀 Market Trends", "🌍 Global Pulse (Bonds & Forex)"])

# ==========================================
# TAB 1: THE ANALYZER 
# ==========================================
with tab1:
    st.subheader("Head-to-Head Analyzer")
    ticker_input = st.text_input("Enter Tickers (Add .TO for Canada! e.g., AAPL, RY.TO, SPY):", "RY.TO")

    if st.button("Analyze with Kbot"):
        with st.spinner("Kbot is pulling the files, drawing charts, and doing the math..."):
            ticker_list = [ticker.strip().upper() for ticker in ticker_input.split(',')]
            all_company_data_for_ai = ""

            for ticker_symbol in ticker_list:
                # We put the disguise on Kbot right here
                stock = yf.Ticker(ticker_symbol, session=safe_session)
                
                try:
                    info = stock.info
                    company_name = info.get('longName', ticker_symbol)
                    current_price = info.get('currentPrice', 'Unknown')
                    industry = info.get('industry', 'ETF / Fund' if 'ETF' in str(info.get('quoteType', '')) else 'Unknown')
                except:
                    # A backup plan just in case Yahoo is still stubborn
                    company_name = ticker_symbol
                    current_price = 'Unknown'
                    industry = 'Unknown'

                raw_news = stock.news
                news_headlines = ""
                if raw_news:
                    for article in raw_news[:5]: 
                        title = article.get('title', 'No Title')
                        news_headlines += f"- {title}\n"

                all_company_data_for_ai += f"Asset: {company_name} ({ticker_symbol}) | Industry: {industry}\nRecent News:\n{news_headlines}\n------\n"

                st.subheader(f"📊 {company_name} ({ticker_symbol})")
                
                try:
                    historical_data = stock.history(period="1y")
                    if current_price == 'Unknown' and not historical_data.empty:
                        current_price = round(historical_data['Close'].iloc[-1], 2)
                    
                    st.write(f"**Current Price:** ${current_price}")

                    fig = go.Figure(data=[go.Candlestick(
                        x=historical_data.index, open=historical_data['Open'],
                        high=historical_data['High'], low=historical_data['Low'], close=historical_data['Close']
                    )])
                    fig.update_layout(title=f"1-Year History: {ticker_symbol}", template="plotly_dark", xaxis_rangeslider_visible=False, height=400)
                    st.plotly_chart(fig, use_container_width=True)
                except:
                    st.warning(f"Could not load chart data for {ticker_symbol}.")

            prompt = f"""
            You are Kbot, a highly intelligent, long-term financial assistant. Your user's name is Kevin.
            Here is the data for the assets: {all_company_data_for_ai}
            
            If ONE asset: Provide a 4-paragraph analysis covering News Sentiment, Business/Fund Strategy, Long-Term Potential, and Risks.
            If MULTIPLE assets: Compare them, discuss risks, and declare a "Winner" for the best long-term hold with an explanation.
            Keep it professional, friendly, and easy to understand.
            """
            response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
            st.divider()
            st.subheader("🧠 Kbot's Executive Summary")
            st.write(response.text)

# ==========================================
# TAB 2: THE DISCOVER TOOL 
# ==========================================
with tab2:
    st.subheader("Discover Safe Long-Term Trends")
    st.write("Kbot will scan the four major economic sectors to find the strongest trends.")
    
    if st.button("Scan the Market"):
        with st.spinner("Kbot is reading macroeconomic news..."):
            sectors = {"Technology": "XLK", "Healthcare": "XLV", "Finance": "XLF", "Energy": "XLE"}
            sector_data = ""
            for sector_name, ticker in sectors.items():
                stock = yf.Ticker(ticker, session=safe_session)
                raw_news = stock.news
                news_headlines = ""
                if raw_news:
                    for article in raw_news[:4]: 
                        news_headlines += f"- {article.get('title', 'No Title')}\n"
                sector_data += f"Sector: {sector_name}\nRecent News:\n{news_headlines}\n------\n"
                
            prompt = f"""
            You are Kbot. Your user is Kevin. Here is the latest news for four market sectors: {sector_data}
            Write a "Market Trend Report":
            1. Summarize news sentiment in each sector.
            2. Identify the strongest, safest long-term sector right now.
            3. Suggest 2 solid, blue-chip companies in that winning sector for Kevin to research.
            """
            response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
            st.divider()
            st.subheader("🧭 Kbot's Market Trend Report")
            st.write(response.text)

# ==========================================
# TAB 3: GLOBAL PULSE
# ==========================================
with tab3:
    st.subheader("Global Pulse: Macroeconomics")
    st.write("Check the health of the global economy by looking at Treasury Bonds and Currency exchange rates.")

    if st.button("Check Global Pulse"):
        with st.spinner("Kbot is checking bond yields and currency exchanges..."):
            macro_symbols = {
                "US 10-Year Treasury Yield": "^TNX",
                "Euro to US Dollar": "EURUSD=X",
                "US Dollar to Canadian Dollar": "CAD=X"
            }

            macro_data_for_ai = ""

            for name, symbol in macro_symbols.items():
                data = yf.Ticker(symbol, session=safe_session)
                try:
                    history = data.history(period="1d")
                    if not history.empty:
                        current_rate = round(history['Close'].iloc[-1], 3)
                        st.write(f"**{name}:** {current_rate}")
                        macro_data_for_ai += f"{name}: {current_rate}\n"
                    else:
                        st.write(f"**{name}:** Data currently unavailable")
                except:
                    st.write(f"**{name}:** Data currently unavailable")

            prompt = f"""
            You are Kbot, speaking to Kevin. 
            Here are the current global macroeconomic indicators:
            {macro_data_for_ai}
            
            Please write a 2-paragraph summary explaining in very simple terms what these specific bond yields and currency rates mean for the overall economy right now, and how they might affect a long-term stock investor.
            """
            
            response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
            st.divider()
            st.subheader("🌍 Kbot's Macro Report")
            st.write(response.text)