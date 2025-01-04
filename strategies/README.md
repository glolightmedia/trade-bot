# Trading Strategies Documentation

## Overview

This directory contains the trading strategies implemented for the bot. Each strategy is designed to align with the bot's goals:
1. Achieve profitability of 10-15% hourly during market hours.
2. Maximize performance during "power hours."
3. Adapt to market conditions for consistent profitability.

The strategies include:
- **DEMA**: Double Exponential Moving Average
- **MACD**: Moving Average Convergence Divergence
- **CCI**: Commodity Channel Index
- **PPO**: Percentage Price Oscillator
- **Breakout**: Identifies price breakouts
- **Mean Reversion**: Capitalizes on price mean reversion
- **Ensemble**: Combines multiple strategies for robust decision-making

---

## Strategies

### **1. Double Exponential Moving Average (DEMA)**

- **Purpose**: Tracks momentum and identifies trends more sensitively than a single EMA.
- **Configuration**:
  - `weight`: Period for calculating DEMA.
  - `thresholds`:
    - `up`: Buy signal threshold.
    - `down`: Sell signal threshold.
- **Goal Alignment**:
  - Quickly adapts to momentum shifts for fast trades during market hours.

---

### **2. Moving Average Convergence Divergence (MACD)**

- **Purpose**: Measures trend strength and potential reversals.
- **Configuration**:
  - `short`: Short EMA period.
  - `long`: Long EMA period.
  - `signal`: Signal line EMA period.
  - `thresholds`:
    - `up`: Buy signal threshold.
    - `down`: Sell signal threshold.
- **Goal Alignment**:
  - Captures trend reversals during volatile periods, optimizing power-hour trades.

---

### **3. Commodity Channel Index (CCI)**

- **Purpose**: Identifies overbought and oversold conditions.
- **Configuration**:
  - `constant`: Multiplier for typical price deviation.
  - `history`: Number of historical periods.
  - `thresholds`:
    - `up`: Overbought threshold (sell signal).
    - `down`: Oversold threshold (buy signal).
- **Goal Alignment**:
  - Exploits extreme price movements to capitalize on corrections.

---

### **4. Percentage Price Oscillator (PPO)**

- **Purpose**: Measures momentum and relative price changes as a percentage.
- **Configuration**:
  - `short`: Short EMA period.
  - `long`: Long EMA period.
  - `signal`: Signal line EMA period.
  - `thresholds`:
    - `up`: Buy signal threshold.
    - `down`: Sell signal threshold.
- **Goal Alignment**:
  - Provides percentage-based signals to ensure scalability across asset classes.

---

### **5. Breakout Strategy**

- **Purpose**: Detects breakouts above resistance or below support levels.
- **Configuration**:
  - `lookback_period`: Period for calculating resistance/support levels.
  - `thresholds`: Optional parameters for additional filtering.
- **Goal Alignment**:
  - Identifies breakout opportunities for high-risk, high-reward trades.

---

### **6. Mean Reversion**

- **Purpose**: Exploits the tendency of prices to revert to their mean.
- **Configuration**:
  - `lookback_period`: Period for calculating moving averages.
  - `thresholds`:
    - `upper_multiplier`: Upper Bollinger Band multiplier.
    - `lower_multiplier`: Lower Bollinger Band multiplier.
- **Goal Alignment**:
  - Targets short-term reversals during range-bound markets.

---

### **7. Ensemble Strategy**

- **Purpose**: Combines signals from multiple strategies using a weighted approach.
- **Configuration**:
  - `weights`: Weighting for each strategy in the ensemble.
- **Goal Alignment**:
  - Balances the strengths of individual strategies for consistent profitability.

---

## Strategy Selection

- Strategies can be dynamically loaded using `strategy_loader.py`.
- Configure each strategy in the `config/strategies/` directory with `.toml` files.

---

## Example Usage

```python
from src.strategies.strategy_loader import StrategyLoader

# Load strategies
loader = StrategyLoader()
loader.load_strategies()

# List available strategies
print("Available Strategies:", loader.list_strategies())

# Use a specific strategy
strategy = loader.get_strategy("dema")
signals = strategy.generate_signals(market_data)
print("Generated Signals:", signals)
