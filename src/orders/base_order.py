import logging
from enum import Enum


class OrderStates(Enum):
    """Enum-like structure for order states."""
    INITIALIZING = "INITIALIZING"
    SUBMITTED = "SUBMITTED"
    MOVING = "MOVING"
    OPEN = "OPEN"
    CHECKING = "CHECKING"
    CHECKED = "CHECKED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    ERROR = "ERROR"


class BaseOrder:
    """Base class for all order types."""

    def __init__(self, api, market):
        self.api = api
        self.market = market
        self.state = OrderStates.INITIALIZING
        self.id = None
        self.completed = False
        self.amount = 0
        self.price = 0
        self.filled_amount = 0
        self.check_interval = 1.5  # in seconds

    def submit(self, side, amount, price):
        """
        Submit an order.
        :param side: 'buy' or 'sell'.
        :param amount: Order amount.
        :param price: Order price.
        """
        try:
            self.amount = amount
            self.price = price
            self.state = OrderStates.SUBMITTED
            logging.info(f"Submitting {side} order: {amount} at {price}")
            response = self.api.place_order(
                side=side,
                amount=amount,
                price=price,
                market=self.market,
            )
            self.id = response.get("id")
            self.state = OrderStates.OPEN
            logging.info(f"Order {self.id} is now OPEN.")
        except Exception as e:
            self.state = OrderStates.ERROR
            logging.error(f"Error submitting order: {e}")
            raise

    def check_order(self):
        """Check the current status of the order."""
        if not self.id:
            logging.error("No order ID to check.")
            return

        try:
            order_status = self.api.get_order_status(self.id)
            if order_status.get("filled"):
                self.filled(order_status["price"])
            elif not order_status.get("open"):
                self.rejected("Order was not executed.")
            else:
                self.state = OrderStates.CHECKED
                logging.info(f"Order {self.id} is still OPEN.")
        except Exception as e:
            self.state = OrderStates.ERROR
            logging.error(f"Error checking order status: {e}")

    def cancel(self):
        """Cancel the order."""
        if not self.id:
            logging.error("No order ID to cancel.")
            return

        try:
            self.api.cancel_order(self.id)
            self.state = OrderStates.CANCELLED
            logging.info(f"Order {self.id} has been CANCELLED.")
        except Exception as e:
            self.state = OrderStates.ERROR
            logging.error(f"Error cancelling order: {e}")

    def rejected(self, reason):
        """Handle order rejection."""
        self.state = OrderStates.REJECTED
        logging.warning(f"Order was rejected: {reason}")

    def filled(self, price):
        """Handle order fulfillment."""
        self.state = OrderStates.FILLED
        self.completed = True
        self.filled_amount = self.amount
        self.price = price
        logging.info(f"Order {self.id} has been FILLED at price {price}.")
