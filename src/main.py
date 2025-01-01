import logging
import json
from datetime import datetime, time as dt_time, timedelta
from alpaca_trade_api import REST
import pandas as pd
import pytz

# Load configuration
with open("config/config.json") as f:
    config = json.load(f)

API_KEY = config["API_KEY"]
SECRET_KEY = config["SECRET_KEY"]
BASE_URL = config["BASE_URL"]
TRADE_SETTINGS = config["TRADE_SETTINGS"]

# Initialize Alpaca API
try:
    api = REST(API_KEY, SECRET_KEY, BASE_URL, api_version=config.get("API_VERSION", "v2"))
    logging.info("Connected to Alpaca API successfully.")
except Exception as e:
    logging.error(f"Failed to connect to Alpaca API: {e}")
    raise

# Define Trading Functions
def get_penny_stocks(api):
    """Fetch all tradable penny stocks."""
    try:
        assets = api.list_assets(status="active")
        return [
            asset.symbol for asset in assets
            if asset.tradable and asset.exchange in ["NYSE", "NASDAQ"] and 0.5 <= asset.last_price <= 5
        ]
    except Exception as e:
        logging.error(f"Error fetching penny stocks: {e}")
        return []

def compute_confidence_score(api, symbol):
    """Compute a confidence score for a stock based on sentiment, technicals, and volume."""
    try:
        bars = api.get_bars(symbol, "1Day", limit=30).df
        indicators = calculate_indicators(bars)
        volume_factor = bars.iloc[-1]["v"] / bars["v"].mean()
        sentiment = fetch_sentiment(symbol)  # Replace with actual sentiment API
        return 0.4 * sentiment + 0.4 * indicators.iloc[-1]["RSI"] / 100 + 0.2 * volume_factor
    except Exception as e:
        logging.warning(f"Error computing confidence score for {symbol}: {e}")
        return 0

def calculate_indicators(data):
    """Calculate SMA and RSI indicators."""
    data["SMA_5"] = data["c"].rolling(window=5).mean()
    data["SMA_15"] = data["c"].rolling(window=15).mean()
    delta = data["c"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data["RSI"] = 100 - (100 / (1 + rs))
    return data

def place_trade(symbol, shares, price):
    """Place a market order for the specified symbol."""
    try:
        api.submit_order(
            symbol=symbol,
            qty=shares,
            side="buy",
            type="market",
            time_in_force="day"
        )
        logging.info(f"Executed trade: {shares} shares of {symbol} at ${price}")
    except Exception as e:
        logging.error(f"Error placing trade for {symbol}: {e}")

def run_bot():
    """Run the trading bot."""
    try:
        penny_stocks = get_penny_stocks(api)
        high_confidence_stocks = []

        for symbol in penny_stocks:
            confidence_score = compute_confidence_score(api, symbol)
            if confidence_score > TRADE_SETTINGS["sentiment_threshold"]:
                high_confidence_stocks.append((symbol, confidence_score))

        high_confidence_stocks = sorted(high_confidence_stocks, key=lambda x: x[1], reverse=True)[:10]
        logging.info(f"High-confidence stocks: {high_confidence_stocks}")

        for stock in high_confidence_stocks:
            symbol, confidence = stock
            price = api.get_last_trade(symbol).price
            allocation = TRADE_SETTINGS["trade_allocation"] * float(api.get_account().buying_power)
            shares_to_buy = int(allocation / price)

            if shares_to_buy > 0:
                place_trade(symbol, shares_to_buy, price)

    except Exception as e:
        logging.error(f"Error during bot execution: {e}")

if __name__ == "__main__":
    run_bot()
