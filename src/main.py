def get_account_balance(api):
    """Fetch the current portfolio balance from Alpaca."""
    try:
        account = api.get_account()
        return float(account.portfolio_value), float(account.buying_power)
    except Exception as e:
        logging.error(f"Error fetching account balance: {e}")
        return 0.0, 0.0

def fetch_active_trades(api):
    """Fetch current holdings from Alpaca."""
    try:
        positions = api.list_positions()
        return [
            {
                "Symbol": pos.symbol,
                "Shares": float(pos.qty),
                "Entry Price": float(pos.avg_entry_price),
                "Current Price": float(pos.current_price),
                "Profit/Loss": float(pos.unrealized_pl)
            }
            for pos in positions
        ]
    except Exception as e:
        logging.error(f"Error fetching active trades: {e}")
        return []

def fetch_high_confidence_stocks(api):
    """Fetch and score all penny stocks dynamically."""
    penny_stocks = get_penny_stocks(api)
    high_confidence_stocks = []

    for symbol in penny_stocks:
        confidence_score = compute_confidence_score(api, symbol)
        if confidence_score > sentiment_threshold:
            high_confidence_stocks.append({"Symbol": symbol, "Confidence Score": confidence_score})

    return sorted(high_confidence_stocks, key=lambda x: x["Confidence Score"], reverse=True)[:10]

def run_bot():
    """Main trading bot logic with after-hours support."""
    try:
        # Fetch balances and active trades
        portfolio_balance, buying_power = get_account_balance(api)
        active_trades = fetch_active_trades(api)
        high_confidence_stocks = fetch_high_confidence_stocks(api)

        logging.info(f"Portfolio Balance: ${portfolio_balance}")
        logging.info(f"Buying Power: ${buying_power}")
        logging.info(f"Active Trades: {active_trades}")
        logging.info(f"High-Confidence Stocks: {high_confidence_stocks}")

        # Trading logic (including after-hours)
        now = datetime.now(pytz.timezone("US/Eastern")).time()
        if PRE_MARKET_OPEN <= now <= AFTER_MARKET_CLOSE:
            for stock in high_confidence_stocks:
                # Example: Trade logic based on buying power and confidence score
                pass  # Replace with trade execution logic
    except Exception as e:
        logging.error(f"Error during bot execution: {e}")
