import pandas as pd
import numpy as np

class BacktestRunner:
    """
    Executes strategies on historical data and generates performance metrics.
    """

    def __init__(self, strategy, initial_balance=10000):
        """
        Initialize the BacktestRunner.
        :param strategy: Strategy instance to test.
        :param initial_balance: Starting balance for the backtest.
        """
        self.strategy = strategy
        self.initial_balance = initial_balance

    def run_backtest(self, data):
        """
        Execute the strategy on historical data.
        :param data: Preprocessed DataFrame with historical market data.
        :return: Dictionary containing results and performance metrics.
        """
        data = self.strategy.generate_signals(data)
        data["Position"] = data["Signal"].shift(1).fillna(0)
        data["PnL"] = data["Position"] * (data["close"].diff().fillna(0))
        data["Equity"] = self.initial_balance + data["PnL"].cumsum()

        metrics = self.calculate_metrics(data)
        return {"results": data, "metrics": metrics}

    def calculate_metrics(self, data):
        """
        Calculate performance metrics for the backtest.
        :param data: DataFrame with backtest results.
        :return: Dictionary of performance metrics.
        """
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
    # Example usage
    from src.strategies.dema import Strategy as DEMA

    # Sample data
    data = pd.DataFrame({
        "timestamp": pd.date_range(start="2023-01-01", periods=100, freq="D"),
        "open": np.random.uniform(100, 200, 100),
        "high": np.random.uniform(150, 250, 100),
        "low": np.random.uniform(50, 100, 100),
        "close": np.random.uniform(100, 200, 100),
    })

    # DEMA strategy configuration
    config = {"weight": 21, "thresholds": {"up": 0.025, "down": -0.025}}
    dema_strategy = DEMA(config)

    # Run backtest
    backtester = BacktestRunner(strategy=dema_strategy)
    results = backtester.run_backtest(data)

    print("Metrics:")
    print(results["metrics"])
    print("\nResults:")
    print(results["results"].head())
