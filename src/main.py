def get_penny_stocks(api):
    """Fetch all tradable penny stocks from Alpaca."""
    try:
        assets = api.list_assets(status="active")
        return [
            asset.symbol for asset in assets
            if asset.tradable and asset.exchange in ["NYSE", "NASDAQ"] and 0.5 <= asset.last_price <= 5
        ]
    except Exception as e:
        logging.error(f"Error fetching penny stocks: {e}")
        return []

def compute_confidence_score(api, symbol):
    """Compute a confidence score based on sentiment, volume, and technicals."""
    try:
        bars = api.get_bars(symbol, "1Day", limit=30).df
        indicators = calculate_indicators(bars)
        sentiment = fetch_sentiment(symbol)
        volume_factor = bars.iloc[-1]["v"] / bars["v"].mean()

        # Adjust weights for your scoring formula
        return (0.4 * sentiment + 0.4 * indicators.iloc[-1]["RSI"] / 100 + 0.2 * volume_factor)
    except Exception as e:
        logging.warning(f"Error computing confidence score for {symbol}: {e}")
        return 0

def run_bot():
    """Main trading bot logic."""
    try:
        penny_stocks = get_penny_stocks(api)
        if not penny_stocks:
            logging.error("No valid penny stocks found. Exiting.")
            return

        high_confidence_stocks = []

        for symbol in penny_stocks:
            confidence_score = compute_confidence_score(api, symbol)
            if confidence_score > sentiment_threshold:
                high_confidence_stocks.append((symbol, confidence_score))

        high_confidence_stocks = sorted(high_confidence_stocks, key=lambda x: x[1], reverse=True)[:10]

        logging.info(f"Top 10 High-Confidence Stocks: {high_confidence_stocks}")
    except Exception as e:
        logging.error(f"Error during bot execution: {e}")
