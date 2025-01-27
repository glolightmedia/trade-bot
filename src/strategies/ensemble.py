import pandas as pd
import numpy as np

class EnsembleStrategy:
    """
    Implements an advanced Ensemble strategy that combines multiple strategies with dynamic weighting,
    confidence scoring, and market-state adaptation. Designed for penny stocks.
    """

    def __init__(self, config, strategies):
        """
        Initialize the Ensemble strategy.
        :param config: Configuration dictionary from TOML file.
        :param strategies: Dictionary of initialized strategy instances (e.g., MACD, RSI, Breakout).
        """
        self.strategies = strategies
        self.base_weights = config["base_weights"]  # Initial strategy weights
        self.performance_window = config.get("performance_window", 24)  # Hours to evaluate strategy performance
        self.confidence_threshold = config.get("confidence_threshold", 0.6)  # Minimum confidence to act
        self.stop_loss = config.get("stop_loss", 0.02)  # 2% stop-loss
        self.take_profit = config.get("take_profit", 0.10)  # 10% take-profit

        # Track strategy performance metrics (e.g., {"MACD": {"success_rate": 0.8, "last_updated": timestamp}})
        self.performance_metrics = {name: {"success_rate": 1.0, "last_updated": None} for name in strategies.keys()}

    def update_weights_based_on_performance(self, data):
        """
        Dynamically adjust strategy weights based on recent performance.
        """
        # Example: Calculate success rates over the last `performance_window` hours
        for strategy_name, strategy in self.strategies.items():
            signals = strategy.generate_signals(data).tail(self.performance_window)
            profitable_trades = (signals["Signal"].shift(1) == 1) & (signals["close"].diff() > 0) | \
                                (signals["Signal"].shift(1) == -1) & (signals["close"].diff() < 0)
            success_rate = profitable_trades.mean()
            self.performance_metrics[strategy_name]["success_rate"] = success_rate if not np.isnan(success_rate) else 0.5

        # Normalize weights based on success rates
        total = sum(self.performance_metrics[name]["success_rate"] for name in self.strategies.keys())
        self.base_weights = {name: (self.performance_metrics[name]["success_rate"] / total) for name in self.strategies.keys()}

    def aggregate_signals(self, data):
        """
        Aggregate signals with dynamic weights and confidence scoring.
        Returns: DataFrame with `Ensemble_Signal`, `Confidence`, `Stop_Loss`, and `Take_Profit`.
        """
        signals = pd.DataFrame(index=data.index)
        signals["Ensemble_Signal"] = 0
        signals["Confidence"] = 0.0
        signals["Stop_Loss"] = np.nan
        signals["Take_Profit"] = np.nan

        for strategy_name, strategy in self.strategies.items():
            strategy_data = strategy.generate_signals(data.copy())
            weight = self.base_weights.get(strategy_name, 0)
            
            # Extract signal, confidence, stop-loss, and take-profit from individual strategies
            signal = strategy_data["Signal"]
            confidence = strategy_data.get("Confidence", 1.0)  # Assume 1.0 if not provided
            sl = strategy_data.get("Stop_Loss", np.nan)
            tp = strategy_data.get("Take_Profit", np.nan)

            # Aggregate signals and confidence
            signals["Ensemble_Signal"] += signal * weight
            signals["Confidence"] += confidence * weight

            # Aggregate tightest stop-loss and take-profit
            signals["Stop_Loss"] = np.where(
                (signal == 1) & (sl < signals["Stop_Loss"]),
                sl,
                signals["Stop_Loss"]
            )
            signals["Take_Profit"] = np.where(
                (signal == 1) & (tp > signals["Take_Profit"]),
                tp,
                signals["Take_Profit"]
            )

        # Normalize confidence and apply threshold
        signals["Confidence"] = signals["Confidence"].clip(0, 1)
        signals["Ensemble_Signal"] = np.where(
            signals["Confidence"] >= self.confidence_threshold,
            np.sign(signals["Ensemble_Signal"]),
            0
        )

        return signals

    def generate_signals(self, data):
        """
        Generate final signals with dynamic weighting and risk parameters.
        """
        self.update_weights_based_on_performance(data)
        signals = self.aggregate_signals(data)
        
        # Default to global stop-loss/take-profit if strategies don't provide them
        signals["Stop_Loss"] = signals["Stop_Loss"].fillna(data["close"] * (1 - self.stop_loss))
        signals["Take_Profit"] = signals["Take_Profit"].fillna(data["close"] * (1 + self.take_profit))
        
        return signals[["Ensemble_Signal", "Confidence", "Stop_Loss", "Take_Profit"]]
