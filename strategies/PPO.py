import pandas as pd

class Strategy:
    """
    Implements the Percentage Price Oscillator (PPO) strategy.
    """

    def __init__(self, config):
        """
        Initialize the PPO strategy with configuration.
        :param config: Configuration dictionary from TOML file.
        """
        self.short_period = config["short"]
        self.long_period = config["long"]
        self.signal_period = config["signal"]
        self.thresholds = config["thresholds"]

    def calculate_ppo(self, data):
        """
        Calculate the PPO line, signal line, and histogram.
        :param data: DataFrame with market data.
        :return: DataFrame with PPO line, signal line, and histogram.
        """
        data["ShortEMA"] = data["close"].ewm(span=self.short_period, adjust=False).mean()
        data["LongEMA"] = data["close"].ewm(span=self.long_period, adjust=False).mean()
        data["PPO_Line"] = ((data["ShortEMA"] - data["LongEMA"]) / data["LongEMA"]) * 100
        data["Signal_Line"] = data["PPO_Line"].ewm(span=self.signal_period, adjust=False).mean()
        data["PPO_Histogram"] = data["PPO_Line"] - data["Signal_Line"]
        return data

    def generate_signals(self, data):
        """
        Generate buy/sell signals based on PPO.
        :param data: DataFrame with market data.
        :return: DataFrame with signals.
        """
        data = self.calculate_ppo(data)
        data["Signal"] = 0
        data.loc[data["PPO_Histogram"] > self.thresholds["up"], "Signal"] = 1  # Buy
        data.loc[data["PPO_Histogram"] < self.thresholds["down"], "Signal"] = -1  # Sell
        return data
