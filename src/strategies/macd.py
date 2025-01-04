import pandas as pd

class Strategy:
    """
    Implements the Moving Average Convergence Divergence (MACD) strategy.
    """

    def __init__(self, config):
        """
        Initialize the MACD strategy with configuration.
        :param config: Configuration dictionary from TOML file.
        """
        self.short_period = config["short"]
        self.long_period = config["long"]
        self.signal_period = config["signal"]
        self.thresholds = config["thresholds"]

    def calculate_macd(self, data):
        """
        Calculate the MACD line and signal line.
        :param data: DataFrame with market data.
        :return: DataFrame with MACD line, signal line, and histogram.
        """
        data["ShortEMA"] = data["close"].ewm(span=self.short_period, adjust=False).mean()
        data["LongEMA"] = data["close"].ewm(span=self.long_period, adjust=False).mean()
        data["MACD_Line"] = data["ShortEMA"] - data["LongEMA"]
        data["Signal_Line"] = data["MACD_Line"].ewm(span=self.signal_period, adjust=False).mean()
        data["MACD_Histogram"] = data["MACD_Line"] - data["Signal_Line"]
        return data

    def generate_signals(self, data):
        """
        Generate buy/sell signals based on MACD.
        :param data: DataFrame with market data.
        :return: DataFrame with signals.
        """
        data = self.calculate_macd(data)
        data["Signal"] = 0
        data.loc[data["MACD_Histogram"] > self.thresholds["up"], "Signal"] = 1  # Buy
        data.loc[data["MACD_Histogram"] < self.thresholds["down"], "Signal"] = -1  # Sell
        return data
