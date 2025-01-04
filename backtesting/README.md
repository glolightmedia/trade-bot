# Backtesting Framework Documentation

## Overview

The backtesting framework provides tools to evaluate and optimize trading strategies using historical data. It allows users to validate strategies, generate insights, and tune parameters to align with the bot's goals:
1. **Profitability**: Test strategies to achieve consistent returns.
2. **Power Hour Optimization**: Analyze market behavior during high-activity periods.
3. **Adaptability**: Refine strategies for different market conditions.

---

## Key Files and Their Roles

### **1. `prepare_date_range.py`**
- **Purpose**: Loads and preprocesses historical market data.
- **Features**:
  - Adds technical indicators like SMA, RSI, and volatility.
  - Filters data by specific date ranges or volatility thresholds.
- **Example Usage**:
  ```python
  from src.backtesting.prepare_date_range import PrepareDateRange

  data = PrepareDateRange.load_historical_data("data/historical/sample_data.csv")
  preprocessed_data = PrepareDateRange.preprocess_data(data)
  filtered_data = PrepareDateRange.filter_by_date_range(preprocessed_data, start_date="2023-01-01", end_date="2023-12-31")
