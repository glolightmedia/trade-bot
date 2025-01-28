import time
import numpy as np
from talib import ATR, RSI, EMA  # Technical analysis library

class HFTStrategy:
    """
    High-Frequency Trading strategy for penny stocks
    Processes 1-minute candles with sub-second decision making
    """
    
    def __init__(self, config, broker, portfolio_manager):
        self.config = config
        self.broker = broker
        self.pm = portfolio_manager
        self.last_trade_time = 0
        self.trade_count = 0
        self.reset_interval = config.get('reset_interval', 3600)  # Reset strategy every hour
        
        # Volatility parameters
        self.atr_period = config.get('atr_period', 14)
        self.min_volatility = config.get('min_volatility', 0.05)  # 5% ATR threshold
        
        # Order parameters
        self.max_trades_per_min = config.get('max_trades_per_min', 30)
        self.slippage_tolerance = config.get('slippage_tolerance', 0.01)
        
        # Initialize indicators
        self.ema_fast = EMA(timeperiod=5)
        self.ema_slow = EMA(timeperiod=20)
        self.rsi = RSI(timeperiod=14)
        
        # State tracking
        self.position = None
        self.last_candle = None

    def calculate_indicators(self, candle):
        """Calculate real-time technical indicators"""
        close = candle['close']
        
        # Update EMAs
        ema_fast = self.ema_fast.update(close)
        ema_slow = self.ema_slow.update(close)
        
        # Calculate volatility
        atr = ATR(candle['high'], candle['low'], close, timeperiod=self.atr_period)[-1]
        rsi = self.rsi.update(close)
        
        return {
            'ema_fast': ema_fast,
            'ema_slow': ema_slow,
            'atr': atr,
            'rsi': rsi
        }

    def generate_signal(self, candle, indicators):
        """Generate HFT signals using multiple conditions"""
        signal = None
        current_time = time.time()
        
        # Volatility check
        if indicators['atr'] < self.min_volatility:
            return None  # Skip low volatility periods
            
        # Trend condition (EMA crossover)
        trend_bullish = indicators['ema_fast'] > indicators['ema_slow']
        trend_bearish = indicators['ema_fast'] < indicators['ema_slow']
        
        # Mean reversion condition (RSI)
        oversold = indicators['rsi'] < 30
        overbought = indicators['rsi'] > 70
        
        # Generate signals
        if trend_bullish and oversold:
            signal = 'BUY'
        elif trend_bearish and overbought:
            signal = 'SELL'
            
        # Rate limiter
        if (current_time - self.last_trade_time) < (60 / self.max_trades_per_min):
            return None
            
        return signal

    def execute_trades(self, signal, candle):
        """Execute trades with slippage control"""
        if signal is None:
            return
            
        price = candle['close']
        position_size = self.calculate_position_size(candle)
        
        try:
            # Market order execution
            if signal == 'BUY':
                order = self.broker.place_market_order(
                    symbol=candle['symbol'],
                    side='BUY',
                    quantity=position_size,
                    slippage=self.slippage_tolerance
                )
                self.position = 'LONG'
                
            elif signal == 'SELL':
                order = self.broker.place_market_order(
                    symbol=candle['symbol'],
                    side='SELL',
                    quantity=position_size,
                    slippage=self.slippage_tolerance
                )
                self.position = 'SHORT'
                
            self.trade_count += 1
            self.last_trade_time = time.time()
            
        except Exception as e:
            self.pm.handle_error(f"Trade failed: {str(e)}")
            
    def calculate_position_size(self, candle):
        """Dynamic position sizing based on volatility"""
        account_balance = self.pm.get_balance()
        risk_per_trade = self.config.get('risk_per_trade', 0.01)  # 1% of account
        atr_value = self.last_candle['atr'] if self.last_candle else candle['atr']
        
        position_size = (account_balance * risk_per_trade) / atr_value
        return round(position_size, 2)  # Round to lot size

    def on_candle(self, candle):
        """Main HFT processing function"""
        self.last_candle = candle
        
        # Reset strategy state periodically
        if (time.time() - self.last_trade_time) > self.reset_interval:
            self._reset_strategy()
            
        indicators = self.calculate_indicators(candle)
        signal = self.generate_signal(candle, indicators)
        self.execute_trades(signal, candle)
        
    def _reset_strategy(self):
        """Reset strategy state to avoid drift"""
        self.ema_fast.reset()
        self.ema_slow.reset()
        self.rsi.reset()
        self.position = None
        self.trade_count = 0
        self.pm.close_all_positions()  # Safety measure

    def should_stop(self):
        """Circuit breaker for excessive losses"""
        daily_pnl = self.pm.get_daily_pnl()
        if daily_pnl < -self.config.get('max_daily_loss', 0.05):  # 5% max loss
            self.pm.close_all_positions()
            return True
        return False
