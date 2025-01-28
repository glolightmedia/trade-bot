import pandas as pd
import numpy as np

class MeanReversionStrategy:
    """
    Implements the Mean Reversion strategy optimized for penny stocks.
    Penny stocks are volatile but often revert to their mean. This strategy focuses on:
    - Identifying overbought/oversold conditions using Bollinger Bands.
    - Incorporating volume and volatility filters to confirm signals.
    - Adding dynamic stop-loss and take-profit levels for risk management.
    """

    def __init__(self, config):
        """
        Initialize the Mean Reversion strategy with configuration.
        :param config: Configuration dictionary from TOML file.
        """
        self.lookback_period = config.get("lookback_period", 20)  # Default lookback period
        self.upper_multiplier = config.get("upper_multiplier", 2.0)  # Multiplier for upper Bollinger Band
        self.lower_multiplier = config.get("lower_multiplier", 2.0)  # Multiplier for lower Bollinger Band
        self.volatility_threshold = config.get("volatility_threshold", 0.05)  # Minimum volatility to trade
        self.volume_threshold = config.get("volume_threshold", 1.5)  # Volume must be 1.5x the average
        self.stop_loss = config.get("stop_loss", 0.02)  # 2% stop-loss
        self.take_profit = config.get("take_profit", 0.10)  # 10% take-profit

    def calculate_mean_reversion(self, data):
        """
        Calculate Bollinger Bands (moving average, upper band, lower band) and volatility.
        :param data: DataFrame with market data (columns: 'close', 'volume').
        :return: DataFrame with Bollinger Bands and volatility.
        """
        # Calculate moving average and standard deviation
        data["Moving_Avg"] = data["close"].rolling(window=self.lookback_period).mean()
        data["Std_Dev"] = data["close"].rolling(window=self.lookback_period).std()

        # Calculate Bollinger Bands
        data["Upper_Band"] = data["Moving_Avg"] + (data["Std_Dev"] * self.upper_multiplier)
        data["Lower_Band"] = data["Moving_Avg"] - (data["Std_Dev"] * self.lower_multiplier)

        # Calculate volatility (standard deviation of price changes)
        data["Volatility"] = data["close"].pct_change().rolling(window=self.lookback_period).std()

        return data

    def confirm_signals(self, data):
        """
        Confirm buy/sell signals using volume and volatility filters.
        :param data: DataFrame with market data.
        :return: DataFrame with confirmed signals.
        """
        # Calculate average volume over the lookback period
        data["Avg_Volume"] = data["volume"].rolling(window=self.lookback_period).mean()

        # Confirm signals if:
        # 1. Price is outside Bollinger Bands AND
        # 2. Volume is above the threshold AND
        # 3. Volatility is above the threshold
        data["Confirmed_Signal"] = np.where(
            ((data["close"] < data["Lower_Band"]) | (data["close"] > data["Upper_Band"])) &
            (data["volume"] > self.volume_threshold * data["Avg_Volume"]) &
            (data["Volatility"] > self.volatility_threshold),
            1,  # Confirmed signal
            0   # No signal
        )

        return data

    def generate_signals(self, data):
        """
        Generate buy/sell signals based on confirmed mean reversion logic.
        :param data: DataFrame with market data.
        :return: DataFrame with signals and stop-loss/take-profit levels.
        """
        # Calculate Bollinger Bands and confirm signals
        data = self.calculate_mean_reversion(data)
        data = self.confirm_signals(data)

        # Initialize signals
        data["Signal"] = 0  # 0 = No signal, 1 = Buy, -1 = Sell

        # Generate buy signals (price below lower band)
        data.loc[
            (data["Confirmed_Signal"] == 1) & (data["close"] < data["Lower_Band"]),
            "Signal"
        ] = 1

        # Generate sell signals (price above upper band)
        data.loc[
            (data["Confirmed_Signal"] == 1) & (data["close"] > data["Upper_Band"]),
            "Signal"
        ] = -1

        # Add stop-loss and take-profit levels
        data["Stop_Loss"] = np.where(
            data["Signal"] == 1,
            data["close"] * (1 - self.stop_loss),  # Stop-loss for long positions
            np.where(
                data["Signal"] == -1,
                data["close"] * (1 + self.stop_loss),  # Stop-loss for short positions
                np.nan
            )
        )

        data["Take_Profit"] = np.where(
            data["Signal"] == 1,
            data["close"] * (1 + self.take_profit),  # Take-profit for long positions
            np.where(
                data["Signal"] == -1,
                data["close"] * (1 - self.take_profit),  # Take-profit for short positions
                np.nan
            )
        )

        return data
