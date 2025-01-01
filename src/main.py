
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
MARKET_HOURS = config["MARKET_HOURS"]

# Initialize Alpaca API
api = REST(API_KEY, SECRET_KEY, BASE_URL, api_version=config.get("API_VERSION", "v2"))

def is_market_open():
    now = datetime.now(pytz.timezone("US/Eastern")).time()
    market_open_time = dt_time.fromisoformat(MARKET_HOURS["MARKET_OPEN"])
    market_close_time = dt_time.fromisoformat(MARKET_HOURS["MARKET_CLOSE"])
    return market_open_time <= now < market_close_time

def get_penny_stocks(api):
    try:
        assets = api.list_assets(status="active")
        penny_stocks = [
            asset.symbol for asset in assets
            if asset.tradable and asset.exchange in ["NYSE", "NASDAQ"]
            and 0.5 <= asset.last_price <= 5
            and asset.volume >= 1_000_000
            and abs(asset.change_percent) > 3
        ]
        return penny_stocks
    except Exception as e:
        logging.error(f"Error fetching penny stocks: {e}")
        return []

def calculate_indicators(data):
    data["SMA_5"] = data["c"].rolling(window=5).mean()
    data["RSI"] = 100 - 100 / (1 + data["c"].diff().clip(lower=0).rolling(14).mean() /
                               data["c"].diff().clip(upper=0).abs().rolling(14).mean())
    data["VWAP"] = (data["v"] * data["c"]).cumsum() / data["v"].cumsum()
    data["ATR"] = data["h"].rolling(window=14).max() - data["l"].rolling(window=14).min()
    return data

def compute_confidence_score(api, symbol):
    try:
        bars = api.get_bars(symbol, "1Day", limit=30).df
        indicators = calculate_indicators(bars)
        volume_factor = bars.iloc[-1]["v"] / bars["v"].mean()
        macd_signal = indicators.iloc[-1]["RSI"]
        vwap = indicators["VWAP"].iloc[-1]
        price = bars["c"].iloc[-1]
        sentiment = fetch_sentiment(symbol)
        confidence_score = (
            0.25 * sentiment +
            0.25 * (indicators.iloc[-1]["RSI"] / 100) +
            0.25 * volume_factor +
            0.15 * (price > vwap) +
            0.1 * (macd_signal > 0)
        )
        return confidence_score
    except Exception as e:
        logging.warning(f"Error computing confidence score for {symbol}: {e}")
        return 0

def fetch_sentiment(symbol):
    try:
        return 0.5  # Placeholder for sentiment API integration
    except Exception as e:
        logging.warning(f"Error fetching sentiment for {symbol}: {e}")
        return 0

def place_trade(symbol, shares, price):
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

def manage_risk():
    try:
        positions = api.list_positions()
        for p in positions:
            if float(p.unrealized_pl) < 0:
                place_trade(p.symbol, p.qty, order_type="sell")
    except Exception as e:
        logging.error(f"Risk management failed: {e}")

def maximize_peak_hours_profitability(api):
    now = datetime.now(pytz.timezone("US/Eastern")).time()
    market_open_time = dt_time.fromisoformat(MARKET_HOURS["MARKET_OPEN"])
    market_close_time = dt_time.fromisoformat(MARKET_HOURS["MARKET_CLOSE"])
    return market_open_time <= now <= (market_open_time + timedelta(hours=2)) or            (market_close_time - timedelta(hours=2)) <= now <= market_close_time

def run_bot():
    manage_risk()
    if not is_market_open():
        logging.info("Market is closed. Running after-hours strategy.")
        run_after_hours_strategy()
        return

    penny_stocks = get_penny_stocks(api)
    if not penny_stocks:
        logging.warning("No penny stocks found. Expanding search.")
        return

    for symbol in penny_stocks:
        bars = api.get_bars(symbol, "1Min", limit=30).df
        if bars.empty:
            continue

        data = calculate_indicators(bars)
        confidence_score = compute_confidence_score(api, symbol)
        if confidence_score > config["TRADE_SETTINGS"]["CONFIDENCE_THRESHOLD"]:
            price = bars["c"].iloc[-1]
            allocation = config["TRADE_SETTINGS"]["TRADE_ALLOCATION"]
            qty = int(allocation / price)
            place_trade(symbol, qty)

def run_after_hours_strategy():
    penny_stocks = get_penny_stocks(api)
    for symbol in penny_stocks:
        sentiment_score = fetch_sentiment(symbol)
        if sentiment_score > 0.7:
            bars = api.get_bars(symbol, "1Min", limit=30).df
            price = bars["c"].iloc[-1]
            vwap = bars["VWAP"].iloc[-1]
            if price < vwap:
                allocation = config["TRADE_SETTINGS"]["AFTER_HOURS_ALLOCATION"]
                qty = int(allocation / price)
                place_trade(symbol, qty)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_bot()
