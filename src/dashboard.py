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
                "Profit/Loss": float(pos.unrealized_pl),
                "Stop Loss": calculate_stop_loss(float(pos.avg_entry_price), float(pos.current_price) * 0.02)
            }
            for pos in positions
        ]
    except Exception as e:
        st.error(f"Error fetching active trades: {e}")
        return []

# Calculate Stop Loss
def calculate_stop_loss(entry_price, atr):
    return entry_price - (1.5 * atr)

# Unified Confidence Score Calculation
def compute_confidence_score(symbol):
    try:
        bars = api.get_bars(symbol, "1Day", limit=30).df
        if bars.empty:
            return 0
        vwap = (bars["c"] * bars["v"]).cumsum() / bars["v"].cumsum()
        rsi = 100 - (100 / (1 + (bars["c"].diff().clip(lower=0).rolling(14).mean() /
                                bars["c"].diff().clip(upper=0).abs().rolling(14).mean())))
        sentiment_score = 0.5  # Placeholder for sentiment API integration
        return (0.4 * sentiment_score + 0.3 * (rsi.iloc[-1] / 100) + 0.3 * (bars.iloc[-1]["c"] > vwap.iloc[-1]))
    except Exception as e:
        st.error(f"Error computing confidence score for {symbol}: {e}")
        return 0

# Fetch High-Confidence Stocks
def fetch_high_confidence_stocks():
    try:
        assets = api.list_assets(status="active")
        high_confidence = []
        for asset in assets:
            if asset.tradable and asset.exchange in ["NYSE", "NASDAQ"]:
                try:
                    last_trade = api.get_last_trade(asset.symbol)
                    price = last_trade.price
                    if 0.5 <= price <= 5:  # Penny stock filter
                        confidence_score = compute_confidence_score(asset.symbol)
                        high_confidence.append({
                            "Symbol": asset.symbol,
                            "Confidence Score (%)": confidence_score,
                            "Current Price": price
                        })
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
high_confidence_stocks = fetch_high_confidence_stocks()
st.table(pd.DataFrame(high_confidence_stocks))

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
profit_trend = pd.DataFrame({
    "Time": ["9:00 AM", "10:00 AM", "11:00 AM", "12:00 PM"],
    "Profit": [100, 200, 150, 300]
})
st.line_chart(profit_trend.set_index("Time"))
