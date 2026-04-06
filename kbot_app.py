# ==========================================
# NEW TAB 4: GOLD & MINING SCANNER (Improved)
# ==========================================
with tab4:
    st.subheader("⛏️ Gold, Silver & Mining Scanner")
    st.caption("1-minute updates • Smart scoring for momentum + volume + relative strength")

    mining_tickers = [
        "GOLD", "NEM", "AEM", "WPM", "FNV", "GFI", "AU", "KGC", "PAAS", "AG",
        "HL", "CDE", "EXK", "MAG", "SIL", "GDX", "GDXJ", "SILJ", "GLD", "SLV",
        "BTG", "EGO", "OR", "NG", "IAU", "PHYS", "AAAU", "BAR", "SGOL"
    ]

    if st.button("🚀 Start Smart Gold & Mining Scanner"):
        placeholder = st.empty()
        
        while True:
            with placeholder.container():
                st.write(f"**Last refreshed:** {datetime.now().strftime('%H:%M:%S')}")

                results = []
                
                for ticker in mining_tickers:
                    try:
                        stock = yf.Ticker(ticker)
                        # Get enough data for indicators
                        hist_5m = stock.history(period="5d", interval="5m")
                        hist_daily = stock.history(period="60d", interval="1d")
                        
                        if len(hist_5m) < 20 or len(hist_daily) < 10:
                            continue
                        
                        # Basic calculations
                        current_price = hist_5m['Close'].iloc[-1]
                        change_5m = (current_price - hist_5m['Close'].iloc[-2]) / hist_5m['Close'].iloc[-2] * 100
                        
                        # Simple momentum score (we'll improve this more later)
                        ema20 = hist_5m['Close'].ewm(span=20).mean().iloc[-1]
                        volume_surge = hist_5m['Volume'].iloc[-1] > hist_5m['Volume'].rolling(20).mean().iloc[-1] * 1.8
                        
                        score = 0
                        if current_price > ema20:
                            score += 40
                        if volume_surge:
                            score += 30
                        if change_5m > 0:
                            score += 20
                        
                        results.append({
                            "Ticker": ticker,
                            "Price": round(current_price, 4),
                            "Change %": round(change_5m, 2),
                            "Score": score,
                            "Volume Surge": "Yes" if volume_surge else "No"
                        })
                    except:
                        continue
                
                if results:
                    df = pd.DataFrame(results)
                    df = df.sort_values(by="Score", ascending=False).reset_index(drop=True)
                    
                    # Highlight top performers
                    st.dataframe(
                        df.style.background_gradient(subset=["Score"], cmap="viridis")
                        .format({"Price": "${:.4f}", "Change %": "{:.2f}%", "Score": "{:.0f}"}),
                        use_container_width=True,
                        height=650
                    )
                    
                    top_picks = df.head(6)["Ticker"].tolist()
                    st.success(f"**Top 6 Right Now:** {', '.join(top_picks)}")
                else:
                    st.warning("Waiting for data...")

            time.sleep(60)