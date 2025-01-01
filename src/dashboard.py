import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Placeholder for integration with the trading bot's logic
# Replace these with live data from your trading bot
portfolio_balance = 100000
active_trades = [
    {"Symbol": "AAPL", "Shares": 50, "Entry Price": 150.5, "Current Price": 152.3, "Profit/Loss": 90},
    {"Symbol": "TSLA", "Shares": 20, "Entry Price": 600, "Current Price": 610, "Profit/Loss": 200},
]
trade_logs = [
    {"Time": "10:00 AM", "Action": "BUY", "Symbol": "AAPL", "Shares": 50, "Price": 150.5},
    {"Time": "10:15 AM", "Action": "SELL", "Symbol": "TSLA", "Shares": 20, "Price": 610},
]
profit_trend = pd.DataFrame({
    "Time": ["9:00 AM", "10:00 AM", "11:00 AM", "12:00 PM"],
    "Profit": [100, 200, 150, 300]
})

# Function to simulate fetching live data (Replace with real API calls)
def fetch_live_data():
    global active_trades, trade_logs
    active_trades.append({
        "Symbol": "GOOG",
        "Shares": 10,
        "Entry Price": 2700,
        "Current Price": 2750,
        "Profit/Loss": 500
    })
    trade_logs.append({
        "Time": "11:30 AM",
        "Action": "BUY",
        "Symbol": "GOOG",
        "Shares": 10,
        "Price": 2700
    })

# Streamlit Dashboard
st.title("Penny Stock Trading Bot Dashboard")

# Portfolio Overview
st.header("Portfolio Overview")
st.metric("Portfolio Balance", f"${portfolio_balance:,.2f}")
st.subheader("Active Trades")
st.dataframe(pd.DataFrame(active_trades))

# Profit & Loss Section
st.header("Profit & Loss")
st.subheader("Trend")
st.line_chart(profit_trend.set_index("Time"))

# Trade Analytics
st.header("Trade Analytics")
profits = [trade["Profit/Loss"] for trade in active_trades]
if profits:
    st.subheader("Profit/Loss Statistics")
    st.write(f"Total Profit: ${sum(profits):,.2f}")
    st.write(f"Average Profit per Trade: ${np.mean(profits):,.2f}")
    st.write(f"Maximum Profit: ${max(profits):,.2f}")
    st.write(f"Minimum Profit: ${min(profits):,.2f}")
else:
    st.write("No profits available to analyze.")

# Trade Execution Logs
st.header("Trade Execution Logs")
st.dataframe(pd.DataFrame(trade_logs))

# Controls
st.header("Trade Settings")
confidence_threshold = st.slider("Confidence Threshold (%)", 0, 100, 70)
max_trades = st.number_input("Max Trades Per Hour", min_value=1, max_value=30, value=10)
stop_loss_factor = st.slider("Stop-Loss Trailing Factor (%)", 0.1, 5.0, 2.0)

# Alerts
st.header("Alerts")
st.warning("Portfolio nearing daily drawdown limit!")
st.success("High-confidence stock opportunity: AAPL")

# Live Data Refresh
if st.button("Refresh Data"):
    fetch_live_data()
    st.experimental_rerun()
