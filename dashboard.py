import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime
from alpaca_trade_api import REST
from src.machine_learning.sentiment_model import SentimentModel
from src.machine_learning.lstm_model import LSTMModel
from src.machine_learning.random_forest import RandomForestModel
from src.plugins.sentiment_plugin import SentimentPlugin

# Load Configuration
try:
    with open("config/config.json") as f:
        config = json.load(f)
except FileNotFoundError:
    st.error("Configuration file 'config/config.json' not found. Ensure it exists.")
    st.stop()

API_KEY = config.get("API_KEY")
SECRET_KEY = config.get("SECRET_KEY")
BASE_URL = config.get("BASE_URL")

# Initialize Alpaca API
try:
    api = REST(API_KEY, SECRET_KEY, BASE_URL, api_version="v2")
except Exception as e:
    st.error(f"Failed to initialize Alpaca API: {e}")
    st.stop()

# Initialize Models and Plugins
try:
    sentiment_model = SentimentModel()
    sentiment_model.load_model("models/pre_trained/vectorizer.pkl", "models/pre_trained/sentiment_model.pkl")

    random_forest = RandomForestModel()
    random_forest.load_model("models/pre_trained/random_forest.pkl")

    lstm_model = LSTMModel(sequence_length=30)
    lstm_model.load_model("models/pre_trained/lstm_model.h5")

    sentiment_plugin = SentimentPlugin()
except FileNotFoundError as e:
    st.error(f"Model file missing: {e}")
    st.stop()
except Exception as e:
    st.error(f"Error initializing models: {e}")
    st.stop()


def fetch_portfolio_overview():
    """Fetches portfolio balance and buying power."""
    try:
        account = api.get_account()
        return float(account.equity), float(account.buying_power)
    except Exception as e:
        st.error(f"Error fetching portfolio overview: {e}")
        return 0, 0


def fetch_active_trades():
    """Fetches active trades with confidence scores."""
    try:
        positions = api.list_positions()
        return [
            {
                "Symbol": pos.symbol,
                "Shares": int(pos.qty),
                "Entry Price": float(pos.avg_entry_price),
                "Current Price": float(pos.current_price),
                "Profit/Loss": float(pos.unrealized_pl),
                "Confidence Score": compute_confidence_score(pos.symbol),
            }
            for pos in positions
        ]
    except Exception as e:
        st.error(f"Error fetching active trades: {e}")
        return []


def compute_confidence_score(symbol):
    """Computes confidence score for a given stock symbol."""
    try:
        bars = api.get_bars(symbol, "1Day", limit=30).df
        if bars.empty:
            return 0

        sentiment = sentiment_plugin.analyze_sentiment(symbol)
        random_forest_score = random_forest.predict(bars)
        lstm_score = lstm_model.predict(bars)

        confidence_score = (
            0.4 * random_forest_score +
            0.4 * lstm_score +
            0.2 * sentiment
        )
        return confidence_score
    except Exception as e:
        st.error(f"Error computing confidence score for {symbol}: {e}")
        return 0


def fetch_high_confidence_stocks():
    """Fetches stocks with the highest confidence scores."""
    try:
        assets = api.list_assets(status="active")
        high_confidence = []
        for asset in assets:
            if asset.tradable and asset.exchange in ["NYSE", "NASDAQ"]:
                last_trade = api.get_last_trade(asset.symbol)
                price = last_trade.price
                if 0.5 <= price <= 5:
                    confidence_score = compute_confidence_score(asset.symbol)
                    high_confidence.append({
                        "Symbol": asset.symbol,
                        "Confidence Score": confidence_score,
                        "Current Price": price
                    })
        return sorted(high_confidence, key=lambda x: x["Confidence Score"], reverse=True)[:5]
    except Exception as e:
        st.error(f"Error fetching high-confidence stocks: {e}")
        return []


def fetch_most_recent_trades():
    """Fetches the most recent trades."""
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


def is_market_open():
    """Checks if the market is open."""
    try:
        clock = api.get_clock()
        return clock.is_open
    except Exception as e:
        st.error(f"Error checking market status: {e}")
        return False


# Streamlit App Configuration
st.set_page_config(
    page_title="Trading Dashboard",
    layout="wide"
)

st.title("📈 Trading Dashboard")

# Portfolio Overview
st.header("💼 Portfolio Overview")
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
st.header("📊 Active Trade Positions")
active_trades = fetch_active_trades()
st.dataframe(pd.DataFrame(active_trades))

# Most Recent Trades
st.subheader("Recent Trades")
recent_trades = fetch_most_recent_trades()
st.table(pd.DataFrame(recent_trades))

# High-Confidence Stocks
st.header("🚀 High-Confidence Stock Opportunities")
high_confidence_stocks = fetch_high_confidence_stocks()
st.table(pd.DataFrame(high_confidence_stocks))
