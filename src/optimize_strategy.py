import pandas as pd
import numpy as np
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score
import time
from src.backtesting.backtest_runner import BacktestRunner
from src.machine_learning.random_forest import RandomForestModel
from src.machine_learning.lstm_model import LSTMModel
from src.machine_learning.sentiment_model import SentimentModel


class OptimizeStrategy:
    """
    Optimizes strategies using machine learning and advanced analytics, with support for real-time adaptation.
    """

    def __init__(self, initial_balance=10000):
        """
        Initialize the strategy optimizer.
        :param initial_balance: Starting balance for backtests.
        """
        self.initial_balance = initial_balance

    def optimize_parameters(self, strategy, data, param_grid):
        """
        Optimize strategy parameters using grid search.
        :param strategy: Strategy instance to optimize.
        :param data: DataFrame with historical market data.
        :param param_grid: Dictionary of parameters to tune.
        :return: Best parameters and performance metrics.
        """
        best_params = None
        best_metrics = None

        for params in self.generate_param_combinations(param_grid):
            strategy.__init__(params)  # Reinitialize strategy with parameters
            backtester = BacktestRunner(strategy, self.initial_balance)
            results = backtester.run_backtest(data)
            metrics = results["metrics"]

            if best_metrics is None or metrics["Total PnL"] > best_metrics["Total PnL"]:
                best_params = params
                best_metrics = metrics

        return best_params, best_metrics

    @staticmethod
    def generate_param_combinations(param_grid):
        """
        Generate all combinations of parameters from a grid.
        :param param_grid: Dictionary of parameter ranges.
        :return: Generator for parameter combinations.
        """
        from itertools import product

        keys = param_grid.keys()
        values = param_grid.values()
        for combination in product(*values):
            yield dict(zip(keys, combination))

    def integrate_ml_predictions(self, strategy, data, ml_model):
        """
        Integrate ML model predictions into the strategy.
        :param strategy: Strategy instance.
        :param data: DataFrame with market data.
        :param ml_model: Trained machine learning model.
        :return: DataFrame with integrated signals.
        """
        data["ML_Signal"] = ml_model.predict(data.drop(columns=["Signal"]))
        data["Integrated_Signal"] = (data["Signal"] + data["ML_Signal"]).apply(lambda x: np.sign(x))
        return data

    def real_time_optimization(self, strategy, data_stream, interval=60):
        """
        Perform real-time strategy optimization.
        :param strategy: Strategy instance.
        :param data_stream: Real-time data stream (e.g., from a broker API).
        :param interval: Time interval (in seconds) for updates.
        """
        while True:
            try:
                real_time_data = data_stream.get_real_time_data()
                optimized_signals = self.integrate_ml_predictions(strategy, real_time_data, ml_model)
                self.execute_trades(optimized_signals)
            except Exception as e:
                print(f"Error in real-time optimization: {e}")
            time.sleep(interval)

    @staticmethod
    def execute_trades(signals):
        """
        Execute trades based on optimized signals.
        :param signals: DataFrame with trading signals.
        """
        for _, row in signals.iterrows():
            if row["Integrated_Signal"] == 1:
                print(f"Executing BUY for {row['asset']} at {row['price']}")
            elif row["Integrated_Signal"] == -1:
                print(f"Executing SELL for {row['asset']} at {row['price']}")

if __name__ == "__main__":
    # Example usage
    from src.strategies.dema import Strategy as DEMA

    # Load sample data
    data = pd.DataFrame({
        "timestamp": pd.date_range(start="2023-01-01", periods=100, freq="D"),
        "open": np.random.uniform(100, 200, 100),
        "high": np.random.uniform(150, 250, 100),
        "low": np.random.uniform(50, 100, 100),
        "close": np.random.uniform(100, 200, 100),
        "Signal": np.random.choice([-1, 0, 1], 100),
    })

    # Initialize strategy and optimizer
    dema_strategy = DEMA({"weight": 21, "thresholds": {"up": 0.025, "down": -0.025}})
    optimizer = OptimizeStrategy()

    # Optimize parameters
    param_grid = {"weight": [20, 21, 22], "thresholds": [{"up": 0.02, "down": -0.02}, {"up": 0.025, "down": -0.025}]}
    best_params, metrics = optimizer.optimize_parameters(dema_strategy, data, param_grid)
    print("Best Parameters:", best_params)
    print("Metrics:", metrics)
