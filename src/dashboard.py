# Portfolio Overview
portfolio_balance, buying_power = get_account_balance(api)
st.header("Portfolio Overview")
st.metric("Portfolio Balance", f"${portfolio_balance:,.2f}")
st.metric("Buying Power", f"${buying_power:,.2f}")

# Active Trades
st.subheader("Active Trades")
active_trades = fetch_active_trades(api)
st.dataframe(pd.DataFrame(active_trades))

# High-Confidence Stocks
st.header("High-Confidence Stock Opportunities")
high_confidence_stocks = fetch_high_confidence_stocks(api)
st.table(pd.DataFrame(high_confidence_stocks))

# Profit/Loss Analytics
st.header("Profit/Loss Analytics")
if active_trades:
    profits = [trade["Profit/Loss"] for trade in active_trades]
    st.write(f"Total Profit: ${sum(profits):,.2f}")
    st.write(f"Average Profit: ${np.mean(profits):,.2f}")
    st.write(f"Maximum Profit: ${max(profits):,.2f}")
    st.write(f"Minimum Profit: ${min(profits):,.2f}")
else:
    st.write("No trades currently active.")

# Profit Trend
st.subheader("Profit Trend")
profit_trend = pd.DataFrame({"Time": ["9 AM", "10 AM", "11 AM"], "Profit": [100, 200, 150]})
st.line_chart(profit_trend.set_index("Time"))
