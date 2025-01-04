import numpy as np
import pandas as pd
from itertools import product

class MultiStrategyOptimizer:
    """
    Compares multiple strategies and tunes their parameters to find optimal configurations.
    """

    def __init__(self, strategies, initial_balance=10000):
        """
        Initialize the optimizer with a set of strategies.
        :param strategies: Dictionary of strategy instances with their names as keys.
        :param initial_balance: Starting balance for backtests.
        """
        self.strategies = strategies
        self.initial_balance = initial_balance

    def evaluate_strategy(self, data, strategy):
        """
        Run a single strategy on historical data and evaluate its performance.
        :param data: Preprocessed DataFrame with historical data.
        :param strategy: Strategy instance.
        :return: Performance metrics for the strategy.
        """
        data = strategy.generate_signals(data)
        data["Position"] = data["Signal"].shift(1).fillna(0)
        data["PnL"] = data["Position"] * (data["close"].diff().fillna(0))
        data["Equity"] = self.initial_balance + data["PnL"].cumsum()

        total_pnl = data["PnL"].sum()
        returns = data["PnL"] / self.initial_balance
        sharpe_ratio = self.calculate_sharpe_ratio(returns)
        max_drawdown = self.calculate_max_drawdown(data["Equity"])
        win_rate = (data["PnL"] > 0).mean()

        return {
            "Total PnL": total_pnl,
            "Sharpe Ratio": sharpe_ratio,
            "Max Drawdown": max_drawdown,
            "Win Rate": win_rate,
        }

    def optimize_parameters(self, data, strategy, param_grid):
        """
        Optimize parameters for a single strategy.
        :param data: Preprocessed DataFrame with historical data.
        :param strategy: Strategy instance.
        :param param_grid: Dictionary of parameters to tune.
        :return: Best parameters and performance metrics.
        """
        param_names = list(param_grid.keys())
        param_combinations = list(product(*param_grid.values()))
        best_metrics = None
        best_params = None

        for params in param_combinations:
            config = dict(zip(param_names, params))
            strategy.__init__(config)  # Reinitialize strategy with new parameters
            metrics = self.evaluate_strategy(data, strategy)

            if best_metrics is None or metrics["Total PnL"] > best_metrics["Total PnL"]:
                best_metrics = metrics
                best_params = config

        return best_params, best_metrics

    def optimize_ensemble(self, data, weights_grid):
        """
        Find the optimal weights for an ensemble of strategies.
        :param data: Preprocessed DataFrame with historical data.
        :param weights_grid: Grid of weights to test for the ensemble.
        :return: Best weights and performance metrics.
        """
        best_metrics = None
        best_weights = None

        for weights in weights_grid:
            ensemble_signals = np.zeros(len(data))
            for i, strategy in enumerate(self.strategies.values()):
                strategy_signals = strategy.generate_signals(data)["Signal"]
                ensemble_signals += weights[i] * strategy_signals

            data["Ensemble_Signal"] = np.sign(ensemble_signals)
            data["Position"] = data["Ensemble_Signal"].shift(1).fillna(0)
            data["PnL"] = data["Position"] * (data["close"].diff().fillna(0))
            data["Equity"] = self.initial_balance + data["PnL"].cumsum()

            total_pnl = data["PnL"].sum()
            sharpe_ratio = self.calculate_sharpe_ratio(data["PnL"] / self.initial_balance)
            max_drawdown = self.calculate_max_drawdown(data["Equity"])

            metrics = {
                "Total PnL": total_pnl,
                "Sharpe Ratio": sharpe_ratio,
                "Max Drawdown": max_drawdown,
            }

            if best_metrics is None or metrics["Total PnL"] > best_metrics["Total PnL"]:
                best_metrics = metrics
                best_weights = weights

        return best_weights, best_metrics

    @staticmethod
    def calculate_sharpe_ratio(returns, risk_free_rate=0.01):
        """
        Calculate the Sharpe ratio.
        :param returns: Series of returns.
        :param risk_free_rate: Risk-free rate of return.
        :return: Sharpe ratio.
        """
        excess_returns = returns - risk_free_rate / 252
        return excess_returns.mean() / excess_returns.std() if excess_returns.std() != 0 else 0

    @staticmethod
    def calculate_max_drawdown(equity_curve):
        """
        Calculate the maximum drawdown.
        :param equity_curve: Series of equity values over time.
        :return: Maximum drawdown as a percentage.
        """
        peak = equity_curve.cummax()
        drawdown = (equity_curve - peak) / peak
        return drawdown.min()


if __name__ == "__main__":
    from src.strategies.dema import Strategy as DEMA
    from src.strategies.macd import Strategy as MACD

    # Sample data
    data = pd.DataFrame({
        "timestamp": pd.date_range(start="2023-01-01", periods=100, freq="D"),
        "open": np.random.uniform(100, 200, 100),
        "high": np.random.uniform(150, 250, 100),
        "low": np.random.uniform(50, 100, 100),
        "close": np.random.uniform(100, 200, 100),
    })

    # Strategy configurations
    dema_config = {"weight": 21, "thresholds": {"up": 0.025, "down": -0.025}}
    macd_config = {"short": 12, "long": 26, "signal": 9, "thresholds": {"up": 0.025, "down": -0.025}}

    strategies = {
        "dema": DEMA(dema_config),
        "macd": MACD(macd_config),
    }

    optimizer = MultiStrategyOptimizer(strategies)

    # Optimize individual strategy parameters
    param_grid = {"weight": [20, 21, 22], "thresholds": [{"up": 0.02, "down": -0.02}, {"up": 0.025, "down": -0.025}]}
    best_params, metrics = optimizer.optimize_parameters(data, strategies["dema"], param_grid)
    print("Best Parameters for DEMA:", best_params)
    print("Metrics:", metrics)

    # Optimize ensemble weights
    weights_grid = [[0.5, 0.5], [0.7, 0.3], [0.3, 0.7]]
    best_weights, ensemble_metrics = optimizer.optimize_ensemble(data, weights_grid)
    print("Best Weights for Ensemble:", best_weights)
    print("Ensemble Metrics:", ensemble_metrics)
