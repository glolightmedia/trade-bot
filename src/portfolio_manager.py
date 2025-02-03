import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from collections import deque

class Portfolio:
    def __init__(self, config, api):
        self.config = config
        self.api = api
        self.balances = {}
        self.fee = None
        self.ticker = None
        self.volatility_data = {}
        self.equity_history = deque(maxlen=1000)  # Track last 1000 equity values
        self.trade_history = []
        self.performance_metrics = {
            'sharpe_ratio': None,
            'max_drawdown': None,
            'win_rate': None
        }
        self.position_sizing_params = config.get("position_sizing", {
            "max_risk_per_trade": 0.01,
            "penny_stock_max_allocation": 0.005,
            "standard_allocation": 0.02,
            "risk_multiplier": 1.5
        })
        
    def initialize_portfolio(self):
        """Initialize portfolio state"""
        self.set_balances()
        self.set_fee()
        self.update_performance_metrics()
        
    def set_balances(self):
        """Fetch and set balances for the portfolio."""
        try:
            full_portfolio = self.api.get_balances()
            self.balances = {
                item["name"]: {"amount": float(item["amount"])}
                for item in full_portfolio
                if item["name"] in [self.config["currency"], self.config["asset"]]
            }
            self._update_equity_history()
            logging.info(f"Balances updated: {self.balances}")
        except Exception as e:
            logging.error(f"Error setting balances: {e}")
            raise

    def set_fee(self):
        """Fetch and set the trading fee."""
        try:
            self.fee = float(self.api.get_fee())
            logging.info(f"Trading fee set to: {self.fee}")
        except Exception as e:
            logging.error(f"Error setting trading fee: {e}")
            raise

    def _update_equity_history(self):
        """Update equity history with current portfolio value"""
        try:
            total = self.convert_balances()["total_balance"]
            self.equity_history.append({
                "timestamp": datetime.now(),
                "equity": total
            })
        except Exception as e:
            logging.error(f"Error updating equity history: {e}")

    def get_equity_history(self):
        """Return equity history as DataFrame"""
        return pd.DataFrame(self.equity_history)

    def calculate_position_size(self, symbol, price, volatility):
        """
        Calculate dynamic position size based on volatility and penny stock status.
        :param symbol: Trading symbol
        :param price: Current price of the asset
        :param volatility: Volatility metric (ATR or standard deviation)
        :return: Position size in shares
        """
        try:
            total_balance = self.convert_balances()["total_balance"]
            max_risk = self.position_sizing_params["max_risk_per_trade"]
            penny_stock_max = self.position_sizing_params["penny_stock_max_allocation"]
            
            # Determine base allocation
            base_allocation = (total_balance * penny_stock_max if price <= 5 
                             else total_balance * self.position_sizing_params["standard_allocation"])
            
            # Volatility adjustment
            volatility_scale = np.clip(1 - (volatility / price), 0.1, 1)
            position_value = base_allocation * volatility_scale * (1 - self.fee)
            
            # Convert to shares with risk management
            max_loss = position_value * max_risk
            shares = max_loss / (volatility * self.position_sizing_params["risk_multiplier"])
            
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

    def update_performance_metrics(self):
        """Calculate key performance metrics"""
        try:
            equity_df = self.get_equity_history()
            returns = equity_df['equity'].pct_change().dropna()
            
            # Sharpe Ratio
            risk_free_rate = 0.02 / 252  # Daily risk-free rate
            self.performance_metrics['sharpe_ratio'] = (
                (returns.mean() - risk_free_rate) / returns.std() * np.sqrt(252)
            )
            
            # Max Drawdown
            cumulative_returns = (1 + returns).cumprod()
            peak = cumulative_returns.expanding(min_periods=1).max()
            drawdown = (cumulative_returns / peak) - 1
            self.performance_metrics['max_drawdown'] = drawdown.min()
            
            # Win Rate (if trade history available)
            if self.trade_history:
                wins = sum(1 for t in self.trade_history if t['profit'] > 0)
                self.performance_metrics['win_rate'] = wins / len(self.trade_history)
                
        except Exception as e:
            logging.error(f"Error updating performance metrics: {e}")

    def rebalance_portfolio(self):
        """Rebalance portfolio based on target allocations"""
        try:
            # Get current positions
            positions = self.api.list_positions()
            
            # Calculate target allocations
            total_equity = self.convert_balances()["total_balance"]
            target_allocation = self.config.get("target_allocation", {})
            
            # Implement rebalancing logic
            for symbol, target in target_allocation.items():
                current_pos = next((p for p in positions if p.symbol == symbol), None)
                current_value = float(current_pos.market_value) if current_pos else 0
                target_value = total_equity * target
                
                if current_value < target_value:
                    # Buy difference
                    price = float(self.api.get_last_trade(symbol).price)
                    shares = int((target_value - current_value) / price)
                    if shares > 0:
                        self.api.submit_order(symbol, shares, "buy", "market", "day")
                elif current_value > target_value:
                    # Sell difference
                    shares = int((current_value - target_value) / float(current_pos.current_price))
                    if shares > 0:
                        self.api.submit_order(symbol, shares, "sell", "market", "day")
                        
        except Exception as e:
            logging.error(f"Error rebalancing portfolio: {e}")

    def record_trade(self, symbol, shares, price, side):
        """Record trade details in history"""
        self.trade_history.append({
            'timestamp': datetime.now(),
            'symbol': symbol,
            'shares': shares,
            'price': price,
            'side': side,
            'fee': self.fee * shares * price
        })

    def get_trade_history(self):
        """Return trade history as DataFrame"""
        return pd.DataFrame(self.trade_history)

    def convert_balances(self):
        """Convert balances into a unified format for analytics."""
        try:
            asset_balance = self.get_balance(self.config["asset"])
            currency_balance = self.get_balance(self.config["currency"])
            total_balance = currency_balance + (asset_balance * self.ticker["bid"])
            return {
                "asset": asset_balance,
                "currency": currency_balance,
                "total_balance": total_balance,
            }
        except Exception as e:
            logging.error(f"Error converting balances: {e}")
            return {
                "asset": 0,
                "currency": 0,
                "total_balance": 0,
            }
