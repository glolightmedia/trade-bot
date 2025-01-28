import logging
import time
import pandas as pd
from datetime import datetime, timedelta

class HFTPlugin:
    """
    High-Frequency Trading (HFT) Plugin for the trading bot.
    This plugin handles HFT-specific tasks such as trade execution, volatility checks, and trade limits.
    """

    def __init__(self, config, api):
        """
        Initialize the HFT plugin with configuration and API.
        :param config: Configuration dictionary from config.json.
        :param api: Alpaca API or other trading API instance.
        """
        self.config = config
        self.api = api
        self.hft_settings = config["TRADE_SETTINGS"]["HFT_SETTINGS"]
        self.trade_limit = self.hft_settings.get("max_trades_per_hour", 30)
        self.volatility_threshold = self.hft_settings.get("volatility_threshold", 0.05)
        self.timeframe = self.hft_settings.get("timeframe", "1Min")
        self.trade_count = 0
        self.last_reset_time = datetime.now()

    def reset_trade_count(self):
        """
        Reset the trade count at the start of each hour.
        """
        current_time = datetime.now()
        if current_time - self.last_reset_time >= timedelta(hours=1):
            self.trade_count = 0
            self.last_reset_time = current_time
            logging.info("HFT trade count reset.")

    def check_trade_limit(self):
        """
        Check if the bot has reached the maximum number of trades per hour.
        :return: True if the limit has not been reached, False otherwise.
        """
        self.reset_trade_count()
        if self.trade_count >= self.trade_limit:
            logging.warning(f"HFT trade limit reached: {self.trade_limit} trades per hour.")
            return False
        return True

    def calculate_volatility(self, data):
        """
        Calculate the volatility of a stock using the Average True Range (ATR).
        :param data: DataFrame with historical price data (columns: 'high', 'low', 'close').
        :return: Volatility (ATR) value.
        """
        high_low = data['high'] - data['low']
        high_close = abs(data['high'] - data['close'].shift())
        low_close = abs(data['low'] - data['close'].shift())
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=14).mean().iloc[-1]
        return atr

    def is_volatile_enough(self, symbol):
        """
        Check if a stock meets the volatility threshold for HFT.
        :param symbol: Stock symbol to check.
        :return: True if the stock is volatile enough, False otherwise.
        """
        try:
            # Fetch historical data for the symbol
            bars = self.api.get_bars(symbol, self.timeframe, limit=15).df
            if bars.empty:
                return False

            # Calculate volatility
            volatility = self.calculate_volatility(bars)
            logging.info(f"Volatility for {symbol}: {volatility:.4f}")

            return volatility >= self.volatility_threshold
        except Exception as e:
            logging.error(f"Error checking volatility for {symbol}: {e}")
            return False

    def execute_trade(self, symbol, signal, price, quantity):
        """
        Execute a trade if all HFT conditions are met.
        :param symbol: Stock symbol to trade.
        :param signal: Trade signal (1 for buy, -1 for sell).
        :param price: Current price of the stock.
        :param quantity: Number of shares to trade.
        """
        try:
            # Check trade limit
            if not self.check_trade_limit():
                return

            # Check volatility
            if not self.is_volatile_enough(symbol):
                logging.warning(f"{symbol} does not meet volatility threshold for HFT.")
                return

            # Execute trade
            if signal == 1:
                self.api.submit_order(symbol, quantity, "buy", "market", "day")
                logging.info(f"HFT Buy Order: {quantity} shares of {symbol} at ${price:.2f}")
            elif signal == -1:
                self.api.submit_order(symbol, quantity, "sell", "market", "day")
                logging.info(f"HFT Sell Order: {quantity} shares of {symbol} at ${price:.2f}")

            # Increment trade count
            self.trade_count += 1
            logging.info(f"HFT trade count: {self.trade_count}/{self.trade_limit}")
        except Exception as e:
            logging.error(f"Error executing HFT trade for {symbol}: {e}")

    def monitor_trades(self):
        """
        Monitor active trades and close positions if necessary.
        """
        try:
            positions = self.api.list_positions()
            for pos in positions:
                symbol = pos.symbol
                current_price = float(pos.current_price)
                entry_price = float(pos.avg_entry_price)
                stop_loss = entry_price * (1 - self.hft_settings.get("stop_loss_trailing_factor", 0.02))

                # Close position if stop-loss is hit
                if current_price <= stop_loss:
                    self.api.submit_order(symbol, pos.qty, "sell", "market", "day")
                    logging.info(f"HFT Stop-Loss Triggered: Sold {pos.qty} shares of {symbol} at ${current_price:.2f}")
        except Exception as e:
            logging.error(f"Error monitoring HFT trades: {e}")
