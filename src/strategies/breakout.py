import pandas as pd

class Strategy:
    """
    Implements the Breakout strategy.
    """

    def __init__(self, config):
        """
        Initialize the Breakout strategy with configuration.
        :param config: Configuration dictionary from TOML file.
        """
        self.lookback_period = config["lookback_period"]
        self.thresholds = config["thresholds"]

    def calculate_breakout_levels(self, data):
        """
        Calculate breakout levels (resistance and support).
        :param data: DataFrame with market data.
        :return: DataFrame with breakout levels.
        """
        data["Resistance"] = data["high"].rolling(window=self.lookback_period).max()
        data["Support"] = data["low"].rolling(window=self.lookback_period).min()
        return data

    def generate_signals(self, data):
        """
        Generate buy/sell signals based on breakout levels.
        :param data: DataFrame with market data.
        :return: DataFrame with signals.
        """
        data = self.calculate_breakout_levels(data)
        data["Signal"] = 0
        data.loc[data["close"] > data["Resistance"], "Signal"] = 1  # Buy
        data.loc[data["close"] < data["Support"], "Signal"] = -1  # Sell
        return data
