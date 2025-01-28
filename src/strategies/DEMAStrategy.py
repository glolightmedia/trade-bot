import pandas as pd

class Strategy:
    """
    Implements the Double Exponential Moving Average (DEMA) strategy.
    """

    def __init__(self, config):
        """
        Initialize the DEMA strategy with configuration.
        :param config: Configuration dictionary from TOML file.
        """
        self.weight = config["weight"]
        self.thresholds = config["thresholds"]

    def calculate_dema(self, data):
        """
        Calculate the Double Exponential Moving Average (DEMA).
        :param data: DataFrame with market data.
        :return: Series with DEMA values.
        """
        ema = data["close"].ewm(span=self.weight, adjust=False).mean()
        dema = 2 * ema - ema.ewm(span=self.weight, adjust=False).mean()
        return dema

    def generate_signals(self, data):
        """
        Generate buy/sell signals based on DEMA.
        :param data: DataFrame with market data.
        :return: DataFrame with signals.
        """
        data["DEMA"] = self.calculate_dema(data)
        data["Signal"] = 0
        data.loc[data["DEMA"] / data["close"] - 1 > self.thresholds["up"], "Signal"] = 1  # Buy
        data.loc[data["DEMA"] / data["close"] - 1 < self.thresholds["down"], "Signal"] = -1  # Sell
        return data
