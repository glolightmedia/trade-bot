# Documentation

This directory contains the documentation for the Penny Stock Trading Bot.

## Overview
The bot is designed to trade penny stocks dynamically based on technical indicators, sentiment analysis, and real-time market conditions.

## Key Features
1. **Technical Indicators**: Utilizes SMA, RSI, MACD, and Stochastic Oscillator for decision-making.
2. **Sentiment Analysis**: Incorporates sentiment from news and social media to assess market conditions.
3. **Dynamic Capital Allocation**: Allocates capital based on confidence scores and predicted growth.
4. **Real-Time Trading**: Trades during market hours and supports pre-market and after-hours trading.
5. **Visualization**: Includes a Streamlit dashboard for monitoring performance and settings.

## File Structure
- **src**: Contains the main trading bot logic and Streamlit dashboard.
- **data**: Stores historical and live trading data.
- **logs**: Logs bot activity and trade execution details.
- **models**: Saves machine learning models used for predictions.
- **config**: Configuration files for API keys and trading settings.
- **tests**: Unit tests to validate bot functionality.

## How to Use
1. Set up the environment by installing required dependencies (refer to `requirements.txt` if available).
2. Update `config/config.json` with your API keys and preferences.
3. Run `src/main.py` to start the trading bot.
4. Launch the dashboard using Streamlit:
   ```bash
   streamlit run src/dashboard.py

