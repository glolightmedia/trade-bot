import pandas as pd
import numpy as np
from datetime import datetime


def load_historical_data(file_path):
    """
    Load historical market data from a file.
    :param file_path: Path to the CSV file.
    :return: DataFrame containing market data.
    """
    try:
        data = pd.read_csv(file_path, parse_dates=["timestamp"])
        data.sort_values("timestamp", inplace=True)
        return data
    except Exception as e:
        raise Exception(f"Error loading historical data: {e}")


def preprocess_data(data):
    """
    Preprocess raw market data for backtesting and machine learning.
    - Adds technical indicators.
    - Normalizes features.
    :param data: DataFrame with raw market data.
    :return: Preprocessed DataFrame.
    """
    try:
        data["SMA_20"] = data["close"].rolling(window=20).mean()
        data["RSI"] = calculate_rsi(data["close"], 14)
        data["Normalized_Close"] = (data["close"] - data["close"].mean()) / data["close"].std()
        return data.dropna()
    except Exception as e:
        raise Exception(f"Error preprocessing data: {e}")


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


def split_data(data, train_ratio=0.8):
    """
    Split data into training and testing sets.
    :param data: DataFrame with preprocessed data.
    :param train_ratio: Ratio of training data to total data.
    :return: Tuple of (train_data, test_data).
    """
    train_size = int(len(data) * train_ratio)
    train_data = data[:train_size]
    test_data = data[train_size:]
    return train_data, test_data


def get_date_range(data, start_date=None, end_date=None):
    """
    Filter data by a specific date range.
    :param data: DataFrame with preprocessed data.
    :param start_date: Start date as a string (YYYY-MM-DD).
    :param end_date: End date as a string (YYYY-MM-DD).
    :return: Filtered DataFrame.
    """
    if start_date:
        data = data[data["timestamp"] >= pd.to_datetime(start_date)]
    if end_date:
        data = data[data["timestamp"] <= pd.to_datetime(end_date)]
    return data


if __name__ == "__main__":
    # Example usage
    file_path = "data/historical/sample_data.csv"
    data = load_historical_data(file_path)

    # Preprocess data
    preprocessed_data = preprocess_data(data)

    # Split into training and testing
    train_data, test_data = split_data(preprocessed_data)

    # Filter by date range
    filtered_data = get_date_range(preprocessed_data, start_date="2023-01-01", end_date="2023-12-31")

    print(f"Training Data: {len(train_data)} rows")
    print(f"Testing Data: {len(test_data)} rows")
    print(f"Filtered Data: {len(filtered_data)} rows")
