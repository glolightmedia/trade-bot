import streamlit as st
import pandas as pd
import numpy as np
from alpaca_trade_api import REST

# Initialize Alpaca API
API_KEY = "Your_Alpaca_API_Key"  # Replace with your actual API Key
SECRET_KEY = "Your_Alpaca_Secret_Key"  # Replace with your actual Secret Key
BASE_URL = "https://paper-api.alpaca.markets"

try:
    api = REST(API_KEY, SECRET_KEY, BASE_URL, api_version="v2")
except Exception as e:
    st.error(f"Failed to connect to Alpaca API: {e}")
    st.stop()

# Define helper functions
def get_account_balance(api):
    """Fetch the current portfolio balance and buying power."""
    try:
        account = api.get_account()
        return float(account.portfolio_value), float(account.buying_power)
    except Exception as e:
        st.error(f"Error fetching account balance: {e}")
        return 0.0, 0.0

def fetch_active_trades(api):
    """Fetch current holdings from Alpaca."""
    try:
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
    except Exception as e:
        st.error(f"Error fetching active trades: {e}")
        return []

def fetch_high_confidence_stocks(api):
    """Placeholder function to fetch high-confidence stocks."""
    # Replace with actual scoring logic
    return [
        {"Symbol": "GOOG", "Confidence Score": 0.85},
        {"Symbol": "AMZN", "Confidence Score": 0.80}
    ]

# Streamlit Dashboard
st.title("Penny Stock Trading Bot Dashboard")

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
profit_trend = pd.DataFrame({"Time": ["9 AM", "10 AM", "11 AM"], "Profit": [100, 200, 150]})
st.line_chart(profit_trend.set_index("Time"))
