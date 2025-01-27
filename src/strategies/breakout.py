import pandas as pd
import numpy as np

class BreakoutStrategy:
    """
    Implements the Breakout strategy optimized for penny stocks.
    Penny stocks often experience sudden price movements, so this strategy focuses on:
    - Identifying strong breakout levels with high confidence.
    - Using dynamic thresholds to adapt to volatility.
    - Incorporating volume spikes to confirm breakouts.
    """

    def __init__(self, config):
        """
        Initialize the Breakout strategy with configuration.
        :param config: Configuration dictionary from TOML file.
        """
        self.lookback_period = config.get("lookback_period", 20)  # Default lookback period
        self.volatility_threshold = config.get("volatility_threshold", 0.05)  # Minimum volatility to consider
        self.volume_multiplier = config.get("volume_multiplier", 2.0)  # Volume spike multiplier
        self.stop_loss = config.get("stop_loss", 0.02)  # 2% stop-loss
        self.take_profit = config.get("take_profit", 0.10)  # 10% take-profit

    def calculate_breakout_levels(self, data):
        """
        Calculate dynamic breakout levels (resistance and support) based on volatility.
        :param data: DataFrame with market data (columns: 'high', 'low', 'close', 'volume').
        :return: DataFrame with breakout levels and volatility.
        """
        # Calculate rolling resistance and support
        data["Resistance"] = data["high"].rolling(window=self.lookback_period).max()
        data["Support"] = data["low"].rolling(window=self.lookback_period).min()

        # Calculate volatility (standard deviation of price changes)
        data["Volatility"] = data["close"].pct_change().rolling(window=self.lookback_period).std()

        return data

    def confirm_breakout(self, data):
        """
        Confirm breakout signals using volume spikes and volatility.
        :param data: DataFrame with market data.
        :return: DataFrame with confirmed breakout signals.
        """
        # Calculate average volume over the lookback period
        data["Avg_Volume"] = data["volume"].rolling(window=self.lookback_period).mean()

        # Confirm breakout if:
        # 1. Price breaks resistance/support AND
        # 2. Volume is above average (spike) AND
        # 3. Volatility is above the threshold
        data["Confirmed_Breakout"] = np.where(
            ((data["close"] > data["Resistance"]) | (data["close"] < data["Support"])) &
            (data["volume"] > self.volume_multiplier * data["Avg_Volume"]) &
            (data["Volatility"] > self.volatility_threshold),
            1,  # Confirmed breakout
            0   # No breakout
        )

        return data

    def generate_signals(self, data):
        """
        Generate buy/sell signals based on confirmed breakouts.
        :param data: DataFrame with market data.
        :return: DataFrame with signals and stop-loss/take-profit levels.
        """
        # Calculate breakout levels and confirm breakouts
        data = self.calculate_breakout_levels(data)
        data = self.confirm_breakout(data)

        # Initialize signals
        data["Signal"] = 0  # 0 = No signal, 1 = Buy, -1 = Sell

        # Generate buy signals (breakout above resistance)
        data.loc[
            (data["Confirmed_Breakout"] == 1) & (data["close"] > data["Resistance"]),
            "Signal"
        ] = 1

        # Generate sell signals (breakout below support)
        data.loc[
            (data["Confirmed_Breakout"] == 1) & (data["close"] < data["Support"]),
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
