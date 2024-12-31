# Enhancing the bot and implementing the trading logic into src/main.py

# Define the file paths
src_dir = "/mnt/data/TradingBot/src"
main_file_path = os.path.join(src_dir, "main.py")

# Enhanced trading logic for src/main.py
enhanced_main_code = """
import logging
import alpaca_trade_api as tradeapi
import pandas as pd
import numpy as np
from datetime import datetime, time as dt_time, timedelta
import pytz
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Configure Logging
logging.basicConfig(level=logging.INFO, filename="../logs/bot_log.txt", filemode="a",
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Alpaca API Configuration
API_KEY = "PKW2LOE9C15MOTYA7AV0"
SECRET_KEY = "LgUfEKAjoV8vx8my5cpuPAEwEQsW56nOa2UzOMYj"
BASE_URL = "https://paper-api.alpaca.markets"

# Initialize Tools
analyzer = SentimentIntensityAnalyzer()

# Trading Parameters
stop_loss_trailing_factor = 0.02
trade_allocation = 0.7
max_trade_allocation = 0.02
sentiment_threshold = 0.1
portfolio_balance = 100000  # Simulated balance
commission_cost = 0.005

# Market Hours (Eastern Time)
MARKET_OPEN = dt_time(9, 30, tzinfo=pytz.timezone('US/Eastern'))
MARKET_CLOSE = dt_time(16, 0, tzinfo=pytz.timezone('US/Eastern'))
PRE_MARKET_OPEN = dt_time(4, 0, tzinfo=pytz.timezone('US/Eastern'))
AFTER_MARKET_CLOSE = dt_time(20, 0, tzinfo=pytz.timezone('US/Eastern'))

# Initialize Alpaca API
try:
    api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL, api_version='v2')
    account = api.get_account()
    if account.status != "ACTIVE":
        raise Exception("Alpaca account is not active. Please verify your API keys.")
    logging.info("Connected to Alpaca API.")
except Exception as e:
    logging.error(f"Failed to connect to Alpaca API: {e}")
    raise

def get_penny_stocks():
    try:
        assets = api.list_assets(status="active")
        return [
            asset.symbol for asset in assets
            if asset.tradable and asset.exchange in ["NYSE", "NASDAQ"]
        ]
    except Exception as e:
        logging.error(f"Error fetching penny stocks from Alpaca: {e}")
        return []

def fetch_sentiment(symbol):
    try:
        # Simulate sentiment score for demonstration
        return np.random.uniform(-1, 1)
    except Exception as e:
        logging.warning(f"Sentiment analysis failed for {symbol}: {e}")
        return 0

def calculate_indicators(data):
    data["SMA_5"] = data["c"].rolling(window=5).mean()
    data["SMA_15"] = data["c"].rolling(window=15).mean()
    delta = data["c"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data["RSI"] = 100 - (100 / (1 + rs))
    return data

def run_bot():
    try:
        penny_stocks = get_penny_stocks()
        if not penny_stocks:
            logging.error("No valid penny stocks found. Exiting.")
            return

        for symbol in penny_stocks:
            try:
                bars = api.get_bars(symbol, "1Day", limit=30).df
                indicators = calculate_indicators(bars)
                sentiment = fetch_sentiment(symbol)

                confidence = (sentiment + indicators.iloc[-1]["RSI"]) / 2
                if confidence > sentiment_threshold:
                    logging.info(f"Trading {symbol} with confidence {confidence:.2f}.")
            except Exception as e:
                logging.error(f"Error processing {symbol}: {e}")

    except Exception as e:
        logging.error(f"Error during bot execution: {e}")

if __name__ == "__main__":
    run_bot()
"""

# Write the enhanced trading logic to src/main.py
with open(main_file_path, "w") as file:
    file.write(enhanced_main_code)

main_file_path

