import logging
from src.portfolio_manager import Portfolio
from src.exchange_utils import isValidOrder, bindAll, retry
import time


class Broker:
    def __init__(self, config, api):
        self.config = config
        self.api = api
        self.market = f"{config['currency'].upper()}{config['asset'].upper()}"
        self.orders = {"open": [], "closed": []}

        if config.get("private"):
            self.portfolio = Portfolio(config, api)
        bindAll(self)

    def can_trade(self):
        # Check if trading is possible
        return self.api.can_trade()

    def can_monitor(self):
        # Check if monitoring is possible
        return self.api.can_monitor()

    def sync(self):
        """Sync the broker with the exchange."""
        if not self.config.get("private"):
            self.set_ticker()
            return

        if not self.can_trade():
            raise Exception("Trading is not possible.")

        self.sync_private_data()

    def sync_private_data(self):
        """Sync private data, like balances and portfolio."""
        tasks = [
            self.set_ticker,
            self.portfolio.set_fee,
            self.portfolio.set_balances,
        ]
        for task in tasks:
            retry(task)

    def set_ticker(self):
        """Fetch the latest ticker data."""
        try:
            self.ticker = self.api.get_ticker()
        except Exception as e:
            logging.error(f"Error fetching ticker: {e}")
            raise

    def create_order(self, order_type, side, amount, parameters=None):
        """Create a new order."""
        if not self.config.get("private"):
            raise Exception("Client is not authenticated.")

        if side not in ["buy", "sell"]:
            raise Exception(f"Unknown side: {side}")

        order_validity = isValidOrder({
            "api": self.api,
            "market": self.market,
            "amount": amount,
            "price": parameters.get("price") if parameters else None,
        })

        if not order_validity["valid"]:
            raise Exception(f"Invalid order: {order_validity['reason']}")

        order = {
            "type": order_type,
            "side": side,
            "amount": amount,
            "parameters": parameters,
            "status": "pending",
        }

        self.execute_order(order)

    def execute_order(self, order):
        """Execute an order and update its status."""
        try:
            response = self.api.place_order(
                order_type=order["type"],
                side=order["side"],
                amount=order["amount"],
                **(order["parameters"] if order["parameters"] else {})
            )
            order["status"] = "completed"
            order["response"] = response
            self.orders["open"].remove(order)
            self.orders["closed"].append(order)
            logging.info(f"Order executed: {order}")
        except Exception as e:
            logging.error(f"Error executing order: {e}")
            order["status"] = "failed"

    def cancel_order(self, order_id):
        """Cancel an existing order."""
        try:
            self.api.cancel_order(order_id)
            logging.info(f"Order {order_id} cancelled.")
        except Exception as e:
            logging.error(f"Error cancelling order {order_id}: {e}")

    def create_trigger(self, trigger_type, on_trigger, props):
        """Create a trading trigger."""
        try:
            return self.api.create_trigger(trigger_type, on_trigger, props)
        except Exception as e:
            logging.error(f"Error creating trigger: {e}")
            raise

