import logging

class Portfolio:
    def __init__(self, config, api):
        self.config = config
        self.api = api
        self.balances = {}
        self.fee = None
        self.ticker = None

    def get_balance(self, fund):
        """Return the balance for a specific fund."""
        return self.balances.get(fund, {"amount": 0})["amount"]

    def set_balances(self):
        """Fetch and set balances for the portfolio."""
        try:
            full_portfolio = self.api.get_balances()
            self.balances = {
                item["name"]: {"amount": item["amount"]}
                for item in full_portfolio
                if item["name"] in [self.config["currency"], self.config["asset"]]
            }
            logging.info(f"Balances updated: {self.balances}")
        except Exception as e:
            logging.error(f"Error setting balances: {e}")
            raise

    def set_fee(self):
        """Fetch and set the trading fee."""
        try:
            self.fee = self.api.get_fee()
            logging.info(f"Trading fee set to: {self.fee}")
        except Exception as e:
            logging.error(f"Error setting trading fee: {e}")
            raise

    def set_ticker(self, ticker):
        """Set the current ticker data."""
        self.ticker = ticker

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
