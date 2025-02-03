import logging
import json
import numpy as np
from datetime import datetime, time as dt_time, timedelta
from alpaca_trade_api import REST
import pandas as pd
import pytz
from src.strategies.strategy_loader import StrategyLoader
from src.machine_learning.random_forest import RandomForestModel
from src.machine_learning.lstm_model import LSTMModel
from src.machine_learning.sentiment_model import SentimentModel
from src.plugins.sentiment_plugin import SentimentPlugin
from src.plugins.hft_plugin import HFTPlugin
from src.portfolio_manager import Portfolio
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

# Initialize Core Components
portfolio = Portfolio(config, api)
strategy_loader = StrategyLoader(config_dir="config/strategies/")
hft_plugin = HFTPlugin(config, api)
sentiment_plugin = SentimentPlugin()

# Load Strategies and ML Models
try:
    strategy_loader.load_strategies()
    strategies = strategy_loader.strategies
    ensemble_strategy = strategies["ensemble"]
    
    # Initialize ML Models
    random_forest = RandomForestModel()
    lstm_model = LSTMModel(sequence_length=30)
    sentiment_model = SentimentModel()
    
    random_forest.load_model(config["MACHINE_LEARNING"]["models"]["random_forest"]["path"])
    lstm_model.load_model(config["MACHINE_LEARNING"]["models"]["lstm_model"]["path"])
    sentiment_model.load_model("models/pre_trained/vectorizer.pkl", 
                             config["MACHINE_LEARNING"]["models"]["sentiment_model"]["path"])
    
except Exception as e:
    logging.error(f"Initialization failed: {e}")
    raise

def is_market_open():
    """Check if the market is open using configurable hours."""
    tz = pytz.timezone("US/Eastern")
    now = datetime.now(tz).time()
    market_open = dt_time.fromisoformat(MARKET_HOURS["MARKET_OPEN"])
    market_close = dt_time.fromisoformat(MARKET_HOURS["MARKET_CLOSE"])
    return market_open <= now <= market_close

def get_penny_stocks():
    """Retrieve volatile penny stocks with liquidity screening."""
    try:
        assets = api.list_assets(status="active")
        return [
            asset.symbol for asset in assets
            if all([
                asset.tradable,
                asset.exchange in ["NYSE", "NASDAQ"],
                0.5 <= asset.last_price <= 5,
                asset.volume >= 1_000_000,
                abs(asset.change_percent) > config["TRADE_SETTINGS"]["HFT_SETTINGS"]["volatility_threshold"]
            ])
        ]
    except Exception as e:
        logging.error(f"Error fetching penny stocks: {e}")
        return []

def calculate_position_size(symbol, price):
    """Calculate dynamic position size using portfolio manager."""
    try:
        bars = api.get_bars(symbol, "1Min", limit=14).df
        if bars.empty:
            return 0
            
        volatility = hft_plugin.calculate_volatility(bars)
        return portfolio.calculate_position_size(symbol, price, volatility)
    except Exception as e:
        logging.error(f"Position sizing failed for {symbol}: {e}")
        return 0

def execute_trade(symbol, signal):
    """Execute trade with HFT optimization and risk management."""
    try:
        bars = api.get_bars(symbol, "1Min", limit=1).df
        if bars.empty:
            return
            
        price = bars["close"].iloc[-1]
        shares = calculate_position_size(symbol, price)
        
        if shares > 0:
            hft_plugin.execute_trade(symbol, signal, price, shares)
            portfolio.update_volatility_metrics(symbol, bars)
    except Exception as e:
        logging.error(f"Trade execution failed for {symbol}: {e}")

def aggregate_signals(symbol):
    """Generate signals using ensemble strategy with real-time data."""
    try:
        bars = api.get_bars(symbol, "1Min", limit=30).df
        if bars.empty:
            return 0
            
        # Get base signals from all strategies
        strategy_signals = {}
        for name, strategy in strategies.items():
            strategy_signals[name] = strategy.generate_signals(bars)
            
        # Get ensemble decision
        ensemble_data = bars.copy()
        for name, signals in strategy_signals.items():
            ensemble_data[f"{name}_signal"] = signals["Signal"]
            
        ensemble_result = ensemble_strategy.generate_signals(ensemble_data)
        
        # Apply ML confidence filter
        if ensemble_result["Confidence"].iloc[-1] < TRADE_SETTINGS["CONFIDENCE_THRESHOLD"]:
            return 0
            
        return ensemble_result["Ensemble_Signal"].iloc[-1]
    except Exception as e:
        logging.error(f"Signal aggregation failed for {symbol}: {e}")
        return 0

def run_bot_cycle():
    """Main trading cycle with HFT optimization."""
    try:
        hft_plugin.monitor_trades()
        portfolio.set_balances()
        
        if not is_market_open():
            logging.info("Market closed - Running after-hours maintenance")
            return
            
        symbols = get_penny_stocks()
        if not symbols:
            logging.info("No qualifying penny stocks found")
            return
            
        for symbol in symbols[:TRADE_SETTINGS["HFT_SETTINGS"]["max_trades_per_hour"]]:
            signal = aggregate_signals(symbol)
            if signal != 0:
                execute_trade(symbol, signal)
                
    except Exception as e:
        logging.error(f"Main trading cycle failed: {e}")

def run_after_hours():
    """After-hours maintenance and strategy optimization."""
    try:
        if config["MACHINE_LEARNING"]["train_models"]:
            lstm_model.retrain()
            random_forest.retrain()
            
        portfolio.rebalance_portfolio()
        strategy_loader.refresh_strategies()
        
    except Exception as e:
        logging.error(f"After-hours maintenance failed: {e}")

if __name__ == "__main__":
    logging.info("Starting Adaptive Trading Bot")
    try:
        while True:
            if is_market_open():
                run_bot_cycle()
                time.sleep(TRADE_SETTINGS["REAL_TIME_ADAPTIVE"]["update_interval_seconds"])
            else:
                run_after_hours()
                time.sleep(300)  # Check every 5 minutes after hours
                
    except KeyboardInterrupt:
        logging.info("Bot shutdown requested")
    except Exception as e:
        logging.critical(f"Critical failure: {e}")
