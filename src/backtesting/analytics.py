import matplotlib.pyplot as plt
import pandas as pd

class Analytics:
    """
    Provides visualizations and performance insights for backtesting results.
    """

    @staticmethod
    def plot_equity_curve(data):
        """
        Plot the equity curve from backtesting results.
        :param data: DataFrame with 'timestamp' and 'Equity' columns.
        """
        plt.figure(figsize=(12, 6))
        plt.plot(data["timestamp"], data["Equity"], label="Equity Curve", color="blue")
        plt.title("Equity Curve")
        plt.xlabel("Time")
        plt.ylabel("Equity Value")
        plt.legend()
        plt.grid()
        plt.show()

    @staticmethod
    def plot_drawdowns(data):
        """
        Plot the drawdowns over time.
        :param data: DataFrame with 'timestamp' and 'Equity' columns.
        """
        data["Peak"] = data["Equity"].cummax()
        data["Drawdown"] = (data["Equity"] - data["Peak"]) / data["Peak"]

        plt.figure(figsize=(12, 6))
        plt.plot(data["timestamp"], data["Drawdown"], label="Drawdown", color="red")
        plt.title("Drawdowns")
        plt.xlabel("Time")
        plt.ylabel("Drawdown (%)")
        plt.legend()
        plt.grid()
        plt.show()

    @staticmethod
    def display_metrics(metrics):
        """
        Display performance metrics in a readable format.
        :param metrics: Dictionary of performance metrics.
        """
        print("\nPerformance Metrics:")
        for key, value in metrics.items():
            print(f"{key}: {value}")

if __name__ == "__main__":
    # Example usage
    data = pd.DataFrame({
        "timestamp": pd.date_range(start="2023-01-01", periods=100, freq="D"),
        "Equity": 10000 + pd.Series(range(100)).cumsum() + pd.Series(range(100)).apply(lambda x: x * -0.5)
    })

    analytics = Analytics()
    analytics.plot_equity_curve(data)
    analytics.plot_drawdowns(data)

    metrics = {
        "Total PnL": 5000,
        "Sharpe Ratio": 1.8,
        "Max Drawdown": -0.15,
        "Win Rate": 0.6,
    }
    analytics.display_metrics(metrics)
