import streamlit as st
import pandas as pd
import numpy as np
from alpaca_trade_api import REST

# Load configuration
import json
with open("config/config.json") as f:
    config = json.load(f)

API_KEY = config["API_KEY"]
SECRET_KEY = config["SECRET_KEY"]
BASE_URL = config["BASE_URL"]

# Initialize Alpaca API
api = REST(API_KEY, SECRET_KEY, BASE_URL, api_version="v2")

# Fetch portfolio balance and buying power
def fetch_portfolio_overview(api):
    account = api.get_account()
    return float(account.portfolio_value), float(account.buying_power)

# Fetch active trades
def fetch_active_trades(api):
    positions = api.list_positions()
    return [
        {
            "Symbol": pos.symbol,
            "Shares": float(pos.qty),
            "Entry Price": float(pos.avg_entry_price),
            "Current Price": float(pos.current_price),
            "Profit/Loss": float(pos.unrealized_pl)
        }
        for pos in positions
    ]

# Fetch high-confidence stocks (placeholder function for now)
@st.cache_data(ttl=60)
def fetch_high_confidence_stocks():
    return [
        {"Symbol": "GOOG", "Confidence Score": 0.85},
        {"Symbol": "AMZN", "Confidence Score": 0.80},
    ]

# Streamlit Dashboard
st.title("Penny Stock Trading Bot Dashboard")

# Portfolio Overview
st.header("Portfolio Overview")
portfolio_balance, buying_power = fetch_portfolio_overview(api)
st.metric("Portfolio Balance", f"${portfolio_balance:,.2f}")
st.metric("Buying Power", f"${buying_power:,.2f}")

# Active Trades
st.subheader("Active Trades")
active_trades = fetch_active_trades(api)
st.dataframe(pd.DataFrame(active_trades))

# High-Confidence Stocks
st.header("High-Confidence Stock Opportunities")
high_confidence_stocks = fetch_high_confidence_stocks()
st.table(pd.DataFrame(high_confidence_stocks))

# Profit/Loss Analytics
st.header("Profit/Loss Analytics")
profits = [trade["Profit/Loss"] for trade in active_trades]
if profits:
    st.write(f"Total Profit: ${sum(profits):,.2f}")
    st.write(f"Average Profit: ${np.mean(profits):,.2f}")
    st.write(f"Maximum Profit: ${max(profits):,.2f}")
    st.write(f"Minimum Profit: ${min(profits):,.2f}")
else:
    st.write("No active trades to analyze.")

# Profit Trend
st.subheader("Profit Trend")
profit_trend = pd.DataFrame({
    "Time": ["9:00 AM", "10:00 AM", "11:00 AM", "12:00 PM"],
    "Profit": [100, 200, 150, 300]
})
st.line_chart(profit_trend.set_index("Time"))

# Alerts Section
st.header("Alerts")
if sum(profits) < -500:  # Replace with dynamic drawdown limits
    st.warning("Portfolio is nearing the daily drawdown limit!")
else:
    st.success("Portfolio is performing well!")

# Real-time control sliders
st.header("Trade Settings")
confidence_threshold = st.slider("Confidence Threshold (%)", 0, 100, 70)
max_trades = st.number_input("Max Trades Per Hour", min_value=1, max_value=30, value=10)
stop_loss_factor = st.slider("Stop-Loss Trailing Factor (%)", 0.1, 5.0, 2.0)

st.write("Use these controls to fine-tune the bot's trading parameters.")
