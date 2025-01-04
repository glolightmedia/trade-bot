import logging
import json
from datetime import datetime, time as dt_time, timedelta
from alpaca_trade_api import REST
import pandas as pd
import numpy as np
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
api = REST(API_KEY, SECRET_KEY, BASE_URL, api_version="v2")

# Trading Parameters
target_hourly_profit = 0.12
stop_loss_trailing_factor = 0.02
max_hourly_trades = 30
trade_allocation = 0.7
confidence_threshold = TRADE_SETTINGS["CONFIDENCE_THRESHOLD"]
trade_log = []
active_positions = {}

# Indicator Functions
def calculate_sma(data, period):
    return data.rolling(window=period).mean()

def calculate_rsi(data, period):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_macd(data, short_period, long_period, signal_period):
    short_ema = data.ewm(span=short_period, adjust=False).mean()
    long_ema = data.ewm(span=long_period, adjust=False).mean()
    macd_line = short_ema - long_ema
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    return macd_line, signal_line, macd_line - signal_line

def calculate_cci(data, period, constant=0.015):
    tp = (data['high'] + data['low'] + data['close']) / 3
    sma = tp.rolling(window=period).mean()
    mad = tp.rolling(window=period).apply(lambda x: np.mean(np.abs(x - x.mean())), raw=False)
    return (tp - sma) / (constant * mad)

def calculate_indicators(data):
    data["SMA_5"] = calculate_sma(data["close"], 5)
    data["SMA_20"] = calculate_sma(data["close"], 20)
    data["RSI"] = calculate_rsi(data["close"], 14)
    data["MACD_Line"], data["MACD_Signal"], data["MACD_Histogram"] = calculate_macd(data["close"], 12, 26, 9)
    data["CCI"] = calculate_cci(data, 20)
    return data

# Market Status
def is_market_open():
    now = datetime.now(pytz.timezone("US/Eastern")).time()
    market_open = dt_time.fromisoformat(MARKET_HOURS["MARKET_OPEN"])
    market_close = dt_time.fromisoformat(MARKET_HOURS["MARKET_CLOSE"])
    return market_open <= now <= market_close

# High-Confidence Stock Finder
def find_high_confidence_stocks():
    assets = api.list_assets(status="active")
    high_confidence_stocks = []

    try:
        snapshots = api.get_snapshots([asset.symbol for asset in assets if asset.tradable])
        for symbol, snapshot in snapshots.items():
            if snapshot and snapshot.daily_bar:
                latest_price = snapshot.daily_bar.c
                confidence_score = snapshot.daily_bar.v / (snapshot.daily_bar.vw * 5)
                if 0.5 <= latest_price <= 5 and confidence_score > confidence_threshold:
                    high_confidence_stocks.append({"symbol": symbol, "price": latest_price, "confidence_score": confidence_score})
    except Exception as e:
        logging.error(f"Error finding high-confidence stocks: {e}")
    return sorted(high_confidence_stocks, key=lambda x: x["confidence_score"], reverse=True)[:30]

# Execute Trade
def execute_trade(symbol, price, allocation):
    qty = int(allocation // price)
    if qty <= 0:
        logging.warning(f"Insufficient funds to trade {symbol}")
        return

    try:
        api.submit_order(symbol, qty, 'buy', 'market', 'day')
        logging.info(f"Bought {qty} shares of {symbol} at ${price:.2f}")
        active_positions[symbol] = {"qty": qty, "buy_price": price}
    except Exception as e:
        logging.error(f"Error trading {symbol}: {e}")

# Monitor and Sell Positions
def monitor_positions():
    global active_positions
    to_sell = []

    for symbol, position in active_positions.items():
        bars = api.get_bars(symbol, "1Min", limit=1).df
        if bars.empty:
            continue
        current_price = bars["close"].iloc[-1]
        if current_price / position["buy_price"] - 1 < -stop_loss_trailing_factor:
            to_sell.append(symbol)

    for symbol in to_sell:
        qty = active_positions[symbol]["qty"]
        api.submit_order(symbol, qty, 'sell', 'market', 'day')
        logging.info(f"Sold {qty} shares of {symbol}")
        del active_positions[symbol]

# Main Bot Execution
def run_bot():
    if not is_market_open():
        logging.info("Market is closed.")
        return

    stocks = find_high_confidence_stocks()
    tradable_balance = api.get_account().buying_power * trade_allocation

    for stock in stocks[:max_hourly_trades]:
        execute_trade(stock["symbol"], stock["price"], tradable_balance / max_hourly_trades)

    monitor_positions()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_bot()
