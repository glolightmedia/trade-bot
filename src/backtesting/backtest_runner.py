import pandas as pd
from src.backtesting.prepare_date_range import preprocess_data, split_data
from sklearn.metrics import accuracy_score, precision_score, recall_score
from datetime import datetime


class BacktestRunner:
    """
    Class to handle backtesting of strategies and machine learning models.
    """

    def __init__(self, strategy, model=None):
        """
        Initialize the BacktestRunner.
        :param strategy: Trading strategy function (e.g., mean_reversion, momentum).
        :param model: Trained machine learning model for predictions (optional).
        """
        self.strategy = strategy
        self.model = model
        self.results = []

    def simulate_trades(self, data):
        """
        Simulate trades based on the provided strategy or ML model.
        :param data: Preprocessed DataFrame with historical data.
        :return: DataFrame with simulated trades and PnL.
        """
        data["Signal"] = self.generate_signals(data)
        data["PnL"] = self.calculate_pnl(data)
        self.results = data
        return data

    def generate_signals(self, data):
        """
        Generate buy/sell signals based on the strategy or ML model.
        :param data: Preprocessed DataFrame with historical data.
        :return: Series with buy (1), sell (-1), or hold (0) signals.
        """
        if self.model:
            features = data[["SMA_20", "RSI", "Normalized_Close"]]
            predictions = self.model.predict(features)
            return predictions
        else:
            return data.apply(self.strategy, axis=1)

    def calculate_pnl(self, data):
        """
        Calculate the profit and loss (PnL) for each trade.
        :param data: DataFrame with signals and market prices.
        :return: Series with PnL values.
        """
        data["Position"] = data["Signal"].shift(1).fillna(0)
        data["PnL"] = data["Position"] * (data["close"].diff().fillna(0))
        return data["PnL"].cumsum()

    def evaluate_performance(self):
        """
        Evaluate the performance of the backtest.
        :return: Dictionary with performance metrics.
        """
        if self.model:
            labels = self.results["Actual"]
            predictions = self.results["Signal"]
            return {
                "Accuracy": accuracy_score(labels, predictions),
                "Precision": precision_score(labels, predictions, average="weighted"),
                "Recall": recall_score(labels, predictions, average="weighted"),
            }
        else:
            total_pnl = self.results["PnL"].iloc[-1]
            win_rate = (self.results["PnL"] > 0).mean()
            return {
                "Total PnL": total_pnl,
                "Win Rate": win_rate,
            }


def run_backtest(data, strategy, model=None):
    """
    Run backtest on historical data using a strategy or ML model.
    :param data: Preprocessed DataFrame with historical data.
    :param strategy: Trading strategy function.
    :param model: Trained ML model (optional).
    :return: Results of the backtest.
    """
    runner = BacktestRunner(strategy, model)
    results = runner.simulate_trades(data)
    performance = runner.evaluate_performance()

    print("Backtest Performance Metrics:")
    for metric, value in performance.items():
        print(f"{metric}: {value}")

    return results, performance


if __name__ == "__main__":
    from src.backtesting.prepare_date_range import load_historical_data, preprocess_data

    # Load and preprocess data
    file_path = "data/historical/sample_data.csv"
    raw_data = load_historical_data(file_path)
    data = preprocess_data(raw_data)

    # Define a sample strategy (e.g., mean reversion)
    def mean_reversion_strategy(row):
        if row["RSI"] < 30:
            return 1  # Buy signal
        elif row["RSI"] > 70:
            return -1  # Sell signal
        else:
            return 0  # Hold signal

    # Run backtest with a sample strategy
    run_backtest(data, strategy=mean_reversion_strategy)
