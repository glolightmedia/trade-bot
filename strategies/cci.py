import pandas as pd

class Strategy:
    """
    Implements the Commodity Channel Index (CCI) strategy.
    """

    def __init__(self, config):
        """
        Initialize the CCI strategy with configuration.
        :param config: Configuration dictionary from TOML file.
        """
        self.constant = config["constant"]
        self.history = config["history"]
        self.thresholds = config["thresholds"]

    def calculate_cci(self, data):
        """
        Calculate the Commodity Channel Index (CCI).
        :param data: DataFrame with market data.
        :return: Series with CCI values.
        """
        tp = (data["high"] + data["low"] + data["close"]) / 3  # Typical Price
        sma = tp.rolling(window=self.history).mean()
        mad = tp.rolling(window=self.history).apply(lambda x: pd.Series(x).mad())
        cci = (tp - sma) / (self.constant * mad)
        return cci

    def generate_signals(self, data):
        """
        Generate buy/sell signals based on CCI.
        :param data: DataFrame with market data.
        :return: DataFrame with signals.
        """
        data["CCI"] = self.calculate_cci(data)
        data["Signal"] = 0
        data.loc[data["CCI"] > self.thresholds["up"], "Signal"] = 1  # Buy
        data.loc[data["CCI"] < self.thresholds["down"], "Signal"] = -1  # Sell
        return data
