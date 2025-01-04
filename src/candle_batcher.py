import pandas as pd
from datetime import datetime

class CandleBatcher:
    """
    Aggregates raw candles into larger timeframes for strategy evaluation.
    """

    def __init__(self, target_interval):
        """
        Initialize the CandleBatcher.
        :param target_interval: Desired aggregation interval in minutes.
        """
        self.target_interval = target_interval

    def aggregate_candles(self, candles):
        """
        Aggregate raw candle data into the target interval.
        :param candles: DataFrame with raw candle data (timestamp, open, high, low, close, volume).
        :return: DataFrame with aggregated candles.
        """
        candles["timestamp"] = pd.to_datetime(candles["timestamp"])
        candles.set_index("timestamp", inplace=True)

        ohlc_dict = {
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum",
        }

        aggregated = candles.resample(f"{self.target_interval}T").agg(ohlc_dict).dropna()
        return aggregated.reset_index()

if __name__ == "__main__":
    # Example usage
    import random

    # Generate sample candle data
    data = {
        "timestamp": [datetime(2023, 1, 1, 0, i).strftime("%Y-%m-%d %H:%M:%S") for i in range(60)],
        "open": [random.uniform(100, 200) for _ in range(60)],
        "high": [random.uniform(200, 300) for _ in range(60)],
        "low": [random.uniform(50, 100) for _ in range(60)],
        "close": [random.uniform(100, 200) for _ in range(60)],
        "volume": [random.randint(1000, 5000) for _ in range(60)],
    }

    raw_candles = pd.DataFrame(data)
    batcher = CandleBatcher(target_interval=15)
    aggregated_candles = batcher.aggregate_candles(raw_candles)

    print("Raw Candles:")
    print(raw_candles.head())
    print("\nAggregated Candles:")
    print(aggregated_candles.head())
