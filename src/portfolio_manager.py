import logging
import numpy as np

class Portfolio:
    def __init__(self, config, api):
        self.config = config
        self.api = api
        self.balances = {}
        self.fee = None
        self.ticker = None
        self.volatility_data = {}  # Stores volatility metrics for symbols
        
    # ... (existing methods remain unchanged) ...

    def calculate_position_size(self, symbol, price, volatility):
        """
        Calculate dynamic position size based on volatility and penny stock status.
        :param symbol: Trading symbol
        :param price: Current price of the asset
        :param volatility: Volatility metric (ATR or standard deviation)
        :return: Position size in shares
        """
        try:
            # Get portfolio balance and risk parameters
            total_balance = self.convert_balances()["total_balance"]
            max_risk = self.config.get("max_risk_per_trade", 0.01)  # 1% of portfolio
            penny_stock_max = self.config.get("penny_stock_max_allocation", 0.005)  # 0.5% for penny stocks
            
            # Determine base allocation
            if price <= 5:  # Penny stock definition
                base_allocation = total_balance * penny_stock_max
            else:
                base_allocation = total_balance * self.config.get("standard_allocation", 0.02)  # 2%
            
            # Volatility adjustment (higher volatility = smaller position)
            volatility_scale = np.clip(1 - (volatility / price), 0.1, 1)
            position_value = base_allocation * volatility_scale * (1 - self.fee)
            
            # Convert to shares and apply risk management
            max_loss = position_value * max_risk
            shares = max_loss / (volatility * self.config.get("risk_multiplier", 1.5))
            
            return int(shares)
            
        except Exception as e:
            logging.error(f"Error calculating position size: {e}")
            return 0

    def update_volatility_metrics(self, symbol, data):
        """
        Update volatility measurements for a symbol
        :param symbol: Trading symbol
        :param data: DataFrame with price history
        """
        try:
            # Calculate 14-period ATR
            high_low = data['high'] - data['low']
            high_close = np.abs(data['high'] - data['close'].shift())
            low_close = np.abs(data['low'] - data['close'].shift())
            tr = np.maximum(high_low, high_close, low_close)
            atr = tr.rolling(window=14).mean().iloc[-1]
            
            # Calculate standard deviation
            returns = data['close'].pct_change().dropna()
            std_dev = returns.std() * np.sqrt(252)  # Annualized
            
            self.volatility_data[symbol] = {
                'atr': atr,
                'std_dev': std_dev,
                'last_updated': datetime.now()
            }
            
        except Exception as e:
            logging.error(f"Error updating volatility metrics: {e}")

    def get_volatility(self, symbol):
        """
        Retrieve current volatility metric for a symbol
        :param symbol: Trading symbol
        :return: ATR value or 0 if not available
        """
        return self.volatility_data.get(symbol, {}).get('atr', 0)
