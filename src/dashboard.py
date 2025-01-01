import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# Simulated Fetch Functions (Replace with Live Data)
@st.cache_data(ttl=60)
def fetch_live_trades():
    return [
        {"Symbol": "AAPL", "Shares": 50, "Entry Price": 150.5, "Current Price": 152.3, "Profit/Loss": 90},
        {"Symbol": "TSLA", "Shares": 20, "Entry Price": 600, "Current Price": 610, "Profit/Loss": 200},
    ]

@st.cache_data(ttl=60)
def fetch_high_confidence_stocks():
    return [
        {"Symbol": "GOOG", "Confidence Score": 85},
        {"Symbol": "AMZN", "Confidence Score": 80},
        {"Symbol": "META", "Confidence Score": 78},
        {"Symbol": "MSFT", "Confidence Score": 76},
        {"Symbol": "NFLX", "Confidence Score": 75},
    ]

@st.cache_data(ttl=60)
def fetch_portfolio_overview():
    return 100000, 50000  # Replace with API Integration

# Streamlit App Configuration
st.set_page_config(
    page_title="Penny Stock Trading Bot",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar Navigation
st.sidebar.title("Navigation")
selected_section = st.sidebar.radio(
    "Go to:", ["Portfolio Overview", "Active Trades", "High-Confidence Stocks", "Profit/Loss Analytics"]
)

# Portfolio Overview Section
if selected_section == "Portfolio Overview":
    st.title("Portfolio Overview")
    portfolio_balance, buying_power = fetch_portfolio_overview()

    col1, col2 = st.columns(2)
    col1.metric("Total Balance", f"${portfolio_balance:,.2f}", "-1.2%")
    col2.metric("Buying Power", f"${buying_power:,.2f}", "2.5%")

# Active Trades Section
if selected_section == "Active Trades":
    st.title("Active Trade Positions")
    active_trades = fetch_live_trades()
    st.dataframe(pd.DataFrame(active_trades))

# High-Confidence Stocks Section
if selected_section == "High-Confidence Stocks":
    st.title("High-Confidence Stock Opportunities")
    high_confidence_stocks = fetch_high_confidence_stocks()
    st.table(pd.DataFrame(high_confidence_stocks))

# Profit/Loss Analytics Section
if selected_section == "Profit/Loss Analytics":
    st.title("Profit/Loss Analytics")

    profits = [trade["Profit/Loss"] for trade in fetch_live_trades()]
    if profits:
        total_profit = sum(profits)
        avg_profit = np.mean(profits)
        max_profit = max(profits)
        min_profit = min(profits)

        st.metric("Total Profit", f"${total_profit:,.2f}")
        st.metric("Average Profit per Trade", f"${avg_profit:,.2f}")
        st.metric("Maximum Profit", f"${max_profit:,.2f}")
        st.metric("Minimum Profit", f"${min_profit:,.2f}")

    # Profit Trend Chart
    profit_trend = pd.DataFrame({
        "Time": ["9:00 AM", "10:00 AM", "11:00 AM", "12:00 PM"],
        "Profit": [100, 200, 150, 300]
    })

    time_filter = st.radio("View Profit Trend for:", ["1D", "1 Week", "1 Month", "6 Months", "1 Year"], horizontal=True)
    st.line_chart(profit_trend.set_index("Time"))

