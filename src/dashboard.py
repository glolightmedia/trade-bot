import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from alpaca_trade_api import REST

# Alpaca API Configuration
API_KEY = "PKW2LOE9C15MOTYA7AV0"
SECRET_KEY = "LgUfEKAjoV8vx8my5cpuPAEwEQsW56nOa2UzOMYj"
BASE_URL = "https://paper-api.alpaca.markets"

api = REST(API_KEY, SECRET_KEY, BASE_URL, api_version="v2")

# Fetch Portfolio Overview
def fetch_portfolio_overview():
    try:
        account = api.get_account()
        return float(account.equity), float(account.buying_power)
    except Exception as e:
        st.error(f"Error fetching portfolio overview: {e}")
        return 0, 0

# Fetch Active Trades
def fetch_active_trades():
    try:
        positions = api.list_positions()
        return [
            {
                "Symbol": pos.symbol,
                "Shares": int(pos.qty),
                "Entry Price": float(pos.avg_entry_price),
                "Current Price": float(pos.current_price),
                "Profit/Loss": float(pos.unrealized_pl)
            }
            for pos in positions
        ]
    except Exception as e:
        st.error(f"Error fetching active trades: {e}")
        return []

# Fetch High-Confidence Stocks
def fetch_high_confidence_stocks():
    try:
        assets = api.list_assets(status="active")
        penny_stocks = [
            asset.symbol for asset in assets
            if asset.tradable and 0.5 <= asset.last_price <= 5 and asset.exchange in ["NYSE", "NASDAQ"]
        ]
        high_confidence = []

        for symbol in penny_stocks:
            try:
                bars = api.get_bars(symbol, "1Day", limit=30).df
                last_close = bars.iloc[-1]["close"]
                confidence_score = np.random.uniform(70, 100)  # Simulated confidence score
                high_confidence.append({"Symbol": symbol, "Confidence Score (%)": confidence_score, "Current Price": last_close})
            except Exception:
                continue

        return sorted(high_confidence, key=lambda x: x["Confidence Score (%)"], reverse=True)[:5]
    except Exception as e:
        st.error(f"Error fetching high-confidence stocks: {e}")
        return []

# Fetch Most Recent Trades
def fetch_most_recent_trades():
    try:
        activities = api.get_activities()
        return [
            {
                "Time": act.transaction_time.strftime("%I:%M %p"),
                "Action": act.side.capitalize(),
                "Symbol": act.symbol,
                "Shares": act.qty,
                "Price": act.price
            }
            for act in activities[:5]
        ]
    except Exception as e:
        st.error(f"Error fetching most recent trades: {e}")
        return []

# Check if Market is Open
def is_market_open():
    try:
        clock = api.get_clock()
        return clock.is_open
    except Exception as e:
        st.error(f"Error checking market status: {e}")
        return False

# Streamlit App Configuration
st.set_page_config(
    page_title="Penny Stock Trading Dashboard",
    layout="wide"
)

# Header Section
st.title("📈 Penny Stock Trading Dashboard")

# Portfolio Overview
st.header("💼 Portfolio Overview")
portfolio_balance, buying_power = fetch_portfolio_overview()
col1, col2 = st.columns(2)
col1.metric("💵 Total Balance", f"${portfolio_balance:,.2f}")
col2.metric("💳 Buying Power", f"${buying_power:,.2f}")

# Market Status Indicator
st.subheader("🕒 Market Status")
if is_market_open():
    st.success("🟢 Market Open")
else:
    st.error("🔴 Market Closed")

# Active Trades
st.header("📊 Active Trade Positions")
active_trades = fetch_active_trades()
st.dataframe(pd.DataFrame(active_trades))

# Most Recent Trades
st.subheader("⏱️ Most Recent Trades")
recent_trades = fetch_most_recent_trades()
st.table(pd.DataFrame(recent_trades))

# High-Confidence Stocks
st.header("🚀 High-Confidence Stock Opportunities")
st.write(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
high_confidence_stocks = fetch_high_confidence_stocks()
st.table(pd.DataFrame(high_confidence_stocks))

# Recommended Buys
st.header("💡 Recommended Buys")
st.write(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
recommended_buys = [
    {
        "Symbol": stock["Symbol"],
        "Current Price": stock["Current Price"],
        "Confidence Score (%)": stock["Confidence Score (%)"]
    }
    for stock in high_confidence_stocks if stock["Confidence Score (%)"] > 80
]
st.table(pd.DataFrame(recommended_buys))

# Profit/Loss Analytics
st.header("📈 Profit/Loss Analytics")
profits = [trade["Profit/Loss"] for trade in active_trades]
if profits:
    st.metric("💰 Total Profit", f"${sum(profits):,.2f}")
    st.metric("📊 Average Profit", f"${np.mean(profits):,.2f}")
    st.metric("📈 Maximum Profit", f"${max(profits):,.2f}")
    st.metric("📉 Minimum Profit", f"${min(profits):,.2f}")

# Profit Trend Chart
st.header("📉 Profit Trend")
time_filter = st.radio("📅 View Profit Trend for:", ["1D", "1 Week", "1 Month", "6 Months", "1 Year"], horizontal=True)
profit_trend = pd.DataFrame({
    "Time": ["9:00 AM", "10:00 AM", "11:00 AM", "12:00 PM"],
    "Profit": [100, 200, 150, 300]
})
st.line_chart(profit_trend.set_index("Time"))


