import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, time as dt_time
import pytz
import time

# Simulated Fetch Functions for Real-Time Updates (Replace with API Integrations)
def fetch_portfolio_overview():
    return 100000, 50000  # Portfolio balance and buying power

def fetch_active_trades():
    return [
        {"Symbol": "AAPL", "Shares": 50, "Entry Price": 150.5, "Current Price": 152.3, "Profit/Loss": 90},
        {"Symbol": "TSLA", "Shares": 20, "Entry Price": 600, "Current Price": 610, "Profit/Loss": 200},
    ]

def fetch_high_confidence_stocks():
    return [
        {"Symbol": "GOOG", "Confidence Score (%)": 85},
        {"Symbol": "AMZN", "Confidence Score (%)": 80},
        {"Symbol": "META", "Confidence Score (%)": 78},
        {"Symbol": "MSFT", "Confidence Score (%)": 76},
        {"Symbol": "NFLX", "Confidence Score (%)": 75},
    ]

def fetch_most_recent_trades():
    return [
        {"Time": "10:00 AM", "Action": "BUY", "Symbol": "AAPL", "Shares": 50, "Price": 150.5},
        {"Time": "10:15 AM", "Action": "SELL", "Symbol": "TSLA", "Shares": 20, "Price": 610},
    ]

def is_market_open():
    now = datetime.now(pytz.timezone("US/Eastern")).time()
    market_open_time = dt_time(9, 30)
    market_close_time = dt_time(16, 0)
    return market_open_time <= now <= market_close_time

# Streamlit App Configuration
st.set_page_config(
    page_title="Penny Stock Trading Dashboard",
    layout="wide"
)

# Header Section
st.title("Penny Stock Trading Dashboard")

# Portfolio Overview
st.header("Portfolio Overview")
portfolio_balance, buying_power = fetch_portfolio_overview()
col1, col2 = st.columns(2)
col1.metric("Total Balance", f"${portfolio_balance:,.2f}")
col2.metric("Buying Power", f"${buying_power:,.2f}")

# Market Status Indicator
st.subheader("Market Status")
if is_market_open():
    st.success("Market Open")
else:
    st.error("Market Closed")

# Active Trades
st.header("Active Trade Positions")
active_trades = fetch_active_trades()
st.dataframe(pd.DataFrame(active_trades))

# Most Recent Trades
st.subheader("Most Recent Trades")
recent_trades = fetch_most_recent_trades()
st.table(pd.DataFrame(recent_trades))

# High-Confidence Stocks
st.header("High-Confidence Stock Opportunities")
high_confidence_stocks = fetch_high_confidence_stocks()
st.write(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.table(pd.DataFrame(high_confidence_stocks))

# Recommended Buys
st.header("Recommended Buys")
recommended_buys = [stock for stock in high_confidence_stocks if stock["Confidence Score (%)"] > 75]
st.write(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.table(pd.DataFrame(recommended_buys))

# Profit/Loss Analytics
st.header("Profit/Loss Analytics")
profits = [trade["Profit/Loss"] for trade in active_trades]
if profits:
    st.metric("Total Profit", f"${sum(profits):,.2f}")
    st.metric("Average Profit", f"${np.mean(profits):,.2f}")
    st.metric("Maximum Profit", f"${max(profits):,.2f}")
    st.metric("Minimum Profit", f"${min(profits):,.2f}")

# Profit Trend Chart
st.header("Profit Trend")
time_filter = st.radio("View Profit Trend for:", ["1D", "1 Week", "1 Month", "6 Months", "1 Year"], horizontal=True)
profit_trend = pd.DataFrame({
    "Time": ["9:00 AM", "10:00 AM", "11:00 AM", "12:00 PM"],
    "Profit": [100, 200, 150, 300]
})
st.line_chart(profit_trend.set_index("Time"))


