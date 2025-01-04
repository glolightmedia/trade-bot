import pandas as pd
import numpy as np
import time
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score, classification_report
from src.backtesting.prepare_date_range import preprocess_data
from src.broker import Broker

class StrategyOptimizer:
    """
    Class to optimize trading strategies using machine learning and real-time evaluation.
    """

    def __init__(self, model=None):
        """
        Initialize the optimizer with an ML model.
        :param model: Machine learning model for predictions.
        """
        self.model = model if model else RandomForestClassifier(random_state=42)

    def optimize_parameters(self, data, param_grid):
        """
        Optimize hyperparameters for the ML model.
        :param data: Preprocessed DataFrame with features and target.
        :param param_grid: Dictionary of hyperparameters to tune.
        :return: Best model and parameters.
        """
        features = data[["SMA_20", "RSI", "Normalized_Close"]]
        target = data["Target"]

        grid_search = GridSearchCV(
            self.model,
            param_grid,
            scoring="precision",
            cv=5,
            n_jobs=-1,
        )
        grid_search.fit(features, target)
        self.model = grid_search.best_estimator_

        print("Best Parameters:", grid_search.best_params_)
        print("Best Score:", grid_search.best_score_)
        return self.model, grid_search.best_params_

    def evaluate_strategy(self, data, strategy_function):
        """
        Evaluate a given strategy and compare it with the ML model.
        :param data: Preprocessed DataFrame with market data.
        :param strategy_function: Existing trading strategy function.
        :return: Comparison of strategy vs. ML model.
        """
        data["ML_Signal"] = self.model.predict(data[["SMA_20", "RSI", "Normalized_Close"]])
        data["Strategy_Signal"] = data.apply(strategy_function, axis=1)

        ml_pnl = self.calculate_pnl(data, "ML_Signal")
        strategy_pnl = self.calculate_pnl(data, "Strategy_Signal")

        print("\nPerformance Comparison:")
        print(f"ML Model PnL: {ml_pnl}")
        print(f"Strategy PnL: {strategy_pnl}")

        if ml_pnl > strategy_pnl:
            print("Recommendation: Use the ML model.")
        else:
            print("Recommendation: Stick with the current strategy.")

        return {"ML_PnL": ml_pnl, "Strategy_PnL": strategy_pnl, "Recommendation": "ML Model" if ml_pnl > strategy_pnl else "Strategy"}

    def calculate_pnl(self, data, signal_column):
        """
        Calculate profit and loss (PnL) based on trading signals.
        :param data: DataFrame with market data and signals.
        :param signal_column: Column name with trading signals.
        :return: Total PnL.
        """
        data["Position"] = data[signal_column].shift(1).fillna(0)
        data["PnL"] = data["Position"] * (data["close"].diff().fillna(0))
        return data["PnL"].sum()

    def real_time_optimization(self, api, strategy_function, interval=60):
        """
        Perform real-time strategy optimization.
        :param api: Trading API for fetching real-time data.
        :param strategy_function: Existing trading strategy function.
        :param interval: Time interval (in seconds) for updates.
        """
        broker = Broker(config={"currency": "USD", "asset": "BTC"}, api=api)

        while True:
            # Fetch real-time data
            try:
                real_time_data = broker.fetch_real_time_data()
                processed_data = preprocess_data(real_time_data)

                # Compare ML predictions with strategy
                processed_data["ML_Signal"] = self.model.predict(processed_data[["SMA_20", "RSI", "Normalized_Close"]])
                processed_data["Strategy_Signal"] = processed_data.apply(strategy_function, axis=1)

                # Evaluate and log performance
                ml_pnl = self.calculate_pnl(processed_data, "ML_Signal")
                strategy_pnl = self.calculate_pnl(processed_data, "Strategy_Signal")

                print(f"ML Model PnL: {ml_pnl}, Strategy PnL: {strategy_pnl}")

                if ml_pnl > strategy_pnl:
                    print("Recommendation: Use the ML model for live trading.")
                else:
                    print("Recommendation: Stick with the current strategy.")

            except Exception as e:
                print(f"Error in real-time optimization: {e}")

            # Wait before the next iteration
            time.sleep(interval)


if __name__ == "__main__":
    from src.backtesting.prepare_date_range import load_historical_data

    # Load and preprocess data
    file_path = "data/historical/sample_data.csv"
    raw_data = load_historical_data(file_path)
    data = preprocess_data(raw_data)
    data["Target"] = (data["close"].shift(-1) > data["close"]).astype(int)  # Binary classification target

    # Initialize optimizer
    optimizer = StrategyOptimizer()

    # Define hyperparameter grid
    param_grid = {
        "n_estimators": [50, 100, 150],
        "max_depth": [10, 20, None],
        "min_samples_split": [2, 5, 10],
    }

    # Optimize model parameters
    print("Optimizing model parameters...")
    model, best_params = optimizer.optimize_parameters(data, param_grid)

    # Define a sample strategy
    def mean_reversion_strategy(row):
        if row["RSI"] < 30:
            return 1  # Buy signal
        elif row["RSI"] > 70:
            return -1  # Sell signal
        else:
            return 0  # Hold signal

    # Run real-time optimization
    print("Starting real-time optimization...")
    optimizer.real_time_optimization(api, mean_reversion_strategy)
