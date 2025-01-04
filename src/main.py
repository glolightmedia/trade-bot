import logging
import json
from datetime import datetime, time as dt_time
from src.broker import Broker
from src.portfolio_manager import Portfolio
from src.exchange_utils import ExchangeUtils
from src.orders.limit_order import LimitOrder
from src.orders.sticky_order import StickyOrder

# Load configuration
with open("config/config.json") as f:
    config = json.load(f)

API_KEY = config["API_KEY"]
SECRET_KEY = config["SECRET_KEY"]
BASE_URL = config["BASE_URL"]
TRADE_SETTINGS = config["TRADE_SETTINGS"]
MARKET_HOURS = config["MARKET_HOURS"]

# Initialize Broker, Portfolio, and Exchange API
from alpaca_trade_api import REST
api = REST(API_KEY, SECRET_KEY, BASE_URL, api_version="v2")
broker = Broker(config, api)
portfolio = Portfolio(config, api)

# Global Trading Parameters
trade_allocation = TRADE_SETTINGS.get("TRADE_ALLOCATION", 0.7)
confidence_threshold = TRADE_SETTINGS.get("CONFIDENCE_THRESHOLD", 0.6)
stop_loss_trailing_factor = TRADE_SETTINGS.get("STOP_LOSS_TRAILING_FACTOR", 0.02)
max_hourly_trades = TRADE_SETTINGS.get("MAX_HOURLY_TRADES", 30)

# Check Market Status
def is_market_open():
    now = datetime.now().time()
    market_open = dt_time.fromisoformat(MARKET_HOURS["MARKET_OPEN"])
    market_close = dt_time.fromisoformat(MARKET_HOURS["MARKET_CLOSE"])
    return market_open <= now <= market_close

# Fetch High-Confidence Stocks
def find_high_confidence_stocks():
    try:
        broker.sync()
        stocks = broker.get_top_stocks(threshold=confidence_threshold)
        logging.info(f"High-confidence stocks: {stocks}")
        return stocks
    except Exception as e:
        logging.error(f"Error finding high-confidence stocks: {e}")
        return []

# Execute Trade Using Advanced Order Types
def execute_trade(stock, allocation):
    try:
        price = stock["price"]
        qty = allocation // price
        if qty <= 0:
            logging.warning(f"Insufficient funds to trade {stock['symbol']}")
            return

        order = LimitOrder(api, broker.market)
        order.create("buy", qty, price)
        logging.info(f"Submitted limit order for {qty} shares of {stock['symbol']} at ${price:.2f}")
    except Exception as e:
        logging.error(f"Error executing trade for {stock['symbol']}: {e}")

# Monitor Positions and Adjust Orders
def monitor_positions():
    try:
        portfolio.set_balances()
        positions = portfolio.convert_balances()

        for symbol, position in positions.items():
            current_price = broker.get_ticker()["price"]
            if current_price / position["buy_price"] - 1 < -stop_loss_trailing_factor:
                broker.sell(symbol, position["qty"])
                logging.info(f"Sold {symbol} due to stop-loss trigger.")
    except Exception as e:
        logging.error(f"Error monitoring positions: {e}")

# Main Trading Bot Logic
def run_bot():
    if not is_market_open():
        logging.info("Market is closed.")
        return

    # Sync Broker and Portfolio
    broker.sync()
    portfolio.set_balances()

    # Get High-Confidence Stocks
    stocks = find_high_confidence_stocks()
    tradable_balance = portfolio.get_balance("USD") * trade_allocation

    # Execute Trades
    for stock in stocks[:max_hourly_trades]:
        execute_trade(stock, tradable_balance / max_hourly_trades)

    # Monitor Positions
    monitor_positions()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_bot()
