import pandas as pd

class Strategy:
    """
    Implements the Mean Reversion strategy.
    """

    def __init__(self, config):
        """
        Initialize the Mean Reversion strategy with configuration.
        :param config: Configuration dictionary from TOML file.
        """
        self.lookback_period = config["lookback_period"]
        self.thresholds = config["thresholds"]

    def calculate_mean_reversion(self, data):
        """
        Calculate the moving average and standard deviation for mean reversion.
        :param data: DataFrame with market data.
        :return: DataFrame with moving average and standard deviation.
        """
        data["Moving_Avg"] = data["close"].rolling(window=self.lookback_period).mean()
        data["Std_Dev"] = data["close"].rolling(window=self.lookback_period).std()
        data["Upper_Band"] = data["Moving_Avg"] + (data["Std_Dev"] * self.thresholds["upper_multiplier"])
        data["Lower_Band"] = data["Moving_Avg"] - (data["Std_Dev"] * self.thresholds["lower_multiplier"])
        return data

    def generate_signals(self, data):
        """
        Generate buy/sell signals based on mean reversion logic.
        :param data: DataFrame with market data.
        :return: DataFrame with signals.
        """
        data = self.calculate_mean_reversion(data)
        data["Signal"] = 0
        data.loc[data["close"] < data["Lower_Band"], "Signal"] = 1  # Buy
        data.loc[data["close"] > data["Upper_Band"], "Signal"] = -1  # Sell
        return data
