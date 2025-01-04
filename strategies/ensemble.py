import pandas as pd

class Strategy:
    """
    Implements the Ensemble strategy that combines multiple strategies.
    """

    def __init__(self, config, strategies):
        """
        Initialize the Ensemble strategy with configuration and individual strategies.
        :param config: Configuration dictionary from TOML file.
        :param strategies: Dictionary of initialized strategy instances.
        """
        self.weights = config["weights"]
        self.strategies = strategies

    def aggregate_signals(self, data):
        """
        Aggregate signals from multiple strategies using a weighted average.
        :param data: DataFrame with market data.
        :return: DataFrame with aggregated signals.
        """
        data["Signal"] = 0
        for strategy_name, strategy in self.strategies.items():
            individual_signals = strategy.generate_signals(data)["Signal"]
            weight = self.weights.get(strategy_name, 1)
            data["Signal"] += individual_signals * weight
        data["Signal"] = data["Signal"].apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
        return data

    def generate_signals(self, data):
        """
        Generate buy/sell signals based on the ensemble logic.
        :param data: DataFrame with market data.
        :return: DataFrame with signals.
        """
        return self.aggregate_signals(data)
