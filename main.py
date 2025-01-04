import logging
import json
from datetime import datetime, time as dt_time
from alpaca_trade_api import REST
import pandas as pd
import pytz
from src.strategies.strategy_loader import StrategyLoader
from src.machine_learning.random_forest import RandomForestModel
from src.machine_learning.lstm_model import LSTMModel
from src.machine_learning.sentiment_model import SentimentModel
from src.plugins.sentiment_plugin import SentimentPlugin
from src.config.logging_config import setup_logging

# Load configuration
with open("config/config.json") as f:
    config = json.load(f)

# Initialize Logging
setup_logging()

API_KEY = config["API_KEY"]
SECRET_KEY = config["SECRET_KEY"]
BASE_URL = config["BASE_URL"]
TRADE_SETTINGS = config["TRADE_SETTINGS"]
MARKET_HOURS = config["MARKET_HOURS"]

# Initialize Alpaca API
api = REST(API_KEY, SECRET_KEY, BASE_URL, api_version="v2")

# Initialize Strategy Loader and Plugins
strategy_loader = StrategyLoader(config_dir="config/strategies/")
strategy_loader.load_strategies()
strategies = strategy_loader.strategies
sentiment_plugin = SentimentPlugin()

# Load ML Models
random_forest = RandomForestModel()
lstm_model = LSTMModel(sequence_length=30)
sentiment_model = SentimentModel()

random_forest.load_model("models/pre_trained/random_forest.pkl")
lstm_model.load_model("models/pre_trained/lstm_model.h5")
sentiment_model.load_model("models/pre_trained/vectorizer.pkl", "models/pre_trained/sentiment_model.pkl")


def is_market_open():
    """Check if the market is open."""
    now = datetime.now(pytz.timezone("US/Eastern")).time()
    market_open_time = dt_time.fromisoformat(MARKET_HOURS["MARKET_OPEN"])
    market_close_time = dt_time.fromisoformat(MARKET_HOURS["MARKET_CLOSE"])
    return market_open_time <= now < market_close_time


def get_penny_stocks(api):
    """Retrieve penny stocks based on volume, price, and volatility."""
    try:
        assets = api.list_assets(status="active")
        return [
            asset.symbol for asset in assets
            if asset.tradable and asset.exchange in ["NYSE", "NASDAQ"]
            and 0.5 <= asset.last_price <= 5
            and asset.volume >= 1_000_000
            and abs(asset.change_percent) > 3
        ]
    except Exception as e:
        logging.error(f"Error fetching penny stocks: {e}")
        return []


def fetch_sentiment(symbol):
    """Fetch sentiment for a given stock symbol."""
    try:
        return sentiment_plugin.analyze_sentiment(symbol)
    except Exception as e:
        logging.error(f"Error fetching sentiment for {symbol}: {e}")
        return 0


def compute_confidence_score(data, symbol):
    """Compute the confidence score using ML models and sentiment analysis."""
    try:
        sentiment = fetch_sentiment(symbol)
        random_forest_score = random_forest.predict(data)
        lstm_score = lstm_model.predict(data)
        final_score = (
            0.4 * random_forest_score +
            0.4 * lstm_score +
            0.2 * sentiment
        )
        return final_score
    except Exception as e:
        logging.warning(f"Error computing confidence score for {symbol}: {e}")
        return 0


def place_trade(symbol, shares):
    """Place a trade using the Alpaca API."""
    try:
        api.submit_order(
            symbol=symbol,
            qty=shares,
            side="buy",
            type="market",
            time_in_force="day"
        )
        logging.info(f"Executed trade: {shares} shares of {symbol}")
    except Exception as e:
        logging.error(f"Error placing trade for {symbol}: {e}")


def run_bot():
    """Run the trading bot."""
    if not is_market_open():
        logging.info("Market is closed. Running after-hours strategy.")
        run_after_hours_strategy()
        return

    penny_stocks = get_penny_stocks(api)
    if not penny_stocks:
        logging.warning("No penny stocks found.")
        return

    for symbol in penny_stocks:
        bars = api.get_bars(symbol, "1Min", limit=30).df
        if bars.empty:
            continue

        data = bars[["open", "high", "low", "close", "volume"]]
        confidence_score = compute_confidence_score(data, symbol)
        if confidence_score > TRADE_SETTINGS["CONFIDENCE_THRESHOLD"]:
            price = bars["close"].iloc[-1]
            allocation = TRADE_SETTINGS["TRADE_ALLOCATION"]
            shares = int(allocation / price)
            place_trade(symbol, shares)


def run_after_hours_strategy():
    """Execute trading strategies during after-hours."""
    penny_stocks = get_penny_stocks(api)
    for symbol in penny_stocks:
        bars = api.get_bars(symbol, "1Min", limit=30).df
        if bars.empty:
            continue

        price = bars["close"].iloc[-1]
        vwap = (bars["volume"] * bars["close"]).cumsum() / bars["volume"].cumsum()
        if price < vwap.iloc[-1]:
            allocation = TRADE_SETTINGS["AFTER_HOURS_ALLOCATION"]
            shares = int(allocation / price)
            place_trade(symbol, shares)


if __name__ == "__main__":
    logging.info("Starting Trading Bot")
    run_bot()
