import pandas as pd
from datetime import datetime

class PrepareDateRange:
    """
    Handles loading, preprocessing, and filtering historical market data.
    """

    @staticmethod
    def load_historical_data(file_path):
        """
        Load historical market data from a CSV file.
        :param file_path: Path to the CSV file.
        :return: DataFrame containing historical market data.
        """
        try:
            data = pd.read_csv(file_path, parse_dates=["timestamp"])
            data.sort_values("timestamp", inplace=True)
            return data
        except Exception as e:
            raise Exception(f"Error loading historical data: {e}")

    @staticmethod
    def preprocess_data(data):
        """
        Preprocess raw market data by adding basic technical indicators.
        :param data: DataFrame with raw market data.
        :return: Preprocessed DataFrame.
        """
        data["SMA_20"] = data["close"].rolling(window=20).mean()
        data["SMA_50"] = data["close"].rolling(window=50).mean()
        data["Volatility"] = data["close"].rolling(window=20).std()
        data["RSI"] = PrepareDateRange.calculate_rsi(data["close"])
        return data.dropna()

    @staticmethod
    def calculate_rsi(prices, period=14):
        """
        Calculate the Relative Strength Index (RSI).
        :param prices: Series of closing prices.
        :param period: Look-back period.
        :return: Series with RSI values.
        """
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def filter_by_date_range(data, start_date=None, end_date=None):
        """
        Filter data by a specific date range.
        :param data: DataFrame with historical data.
        :param start_date: Start date as a string (YYYY-MM-DD).
        :param end_date: End date as a string (YYYY-MM-DD).
        :return: Filtered DataFrame.
        """
        if start_date:
            data = data[data["timestamp"] >= pd.to_datetime(start_date)]
        if end_date:
            data = data[data["timestamp"] <= pd.to_datetime(end_date)]
        return data

    @staticmethod
    def filter_by_volatility(data, threshold):
        """
        Filter data by high volatility.
        :param data: DataFrame with historical data.
        :param threshold: Volatility threshold.
        :return: Filtered DataFrame.
        """
        return data[data["Volatility"] > threshold]


if __name__ == "__main__":
    # Example usage
    file_path = "data/historical/sample_data.csv"
    processor = PrepareDateRange()

    # Load data
    data = processor.load_historical_data(file_path)

    # Preprocess data
    preprocessed_data = processor.preprocess_data(data)

    # Filter by date range
    filtered_data = processor.filter_by_date_range(preprocessed_data, start_date="2023-01-01", end_date="2023-12-31")

    # Filter by high volatility
    high_volatility_data = processor.filter_by_volatility(filtered_data, threshold=5)

    print("Filtered Data by Date Range:")
    print(filtered_data.head())

    print("\nHigh Volatility Data:")
    print(high_volatility_data.head())
