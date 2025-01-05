import numpy as np
import pandas as pd
import logging

class VolatilityPlugin:
    """
    Plugin to analyze market volatility and generate insights.
    """

    def __init__(self, lookback_period=20):
        self.lookback_period = lookback_period

    def calculate_volatility(self, data):
        """
        Calculate volatility using the standard deviation of returns.
        :param data: A pandas DataFrame with a 'close' column.
        :return: Volatility as a percentage.
        """
        try:
            if 'close' not in data.columns:
                raise ValueError("Data must include a 'close' column.")

            # Calculate daily returns
            data['returns'] = data['close'].pct_change()

            # Calculate rolling standard deviation of returns
            volatility = data['returns'].rolling(window=self.lookback_period).std()

            # Convert to percentage
            return volatility * 100
        except Exception as e:
            logging.error(f"Error calculating volatility: {e}")
            return pd.Series()

    def is_high_volatility(self, data, threshold=2.0):
        """
        Determine if the market is in a high-volatility state.
        :param data: A pandas DataFrame with a 'close' column.
        :param threshold: The volatility threshold percentage.
        :return: True if high volatility, False otherwise.
        """
        try:
            volatility = self.calculate_volatility(data)
            if volatility.empty:
                return False

            # Check if the latest volatility exceeds the threshold
            return volatility.iloc[-1] > threshold
        except Exception as e:
            logging.error(f"Error determining high volatility: {e}")
            return False
