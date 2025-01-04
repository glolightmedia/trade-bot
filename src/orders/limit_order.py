import logging
from src.orders.base_order import BaseOrder, OrderStates


class LimitOrder(BaseOrder):
    """Class for managing limit orders."""

    def __init__(self, api, market, post_only=True):
        """
        Initialize the LimitOrder.
        :param api: API instance for exchange interactions.
        :param market: Market information.
        :param post_only: Whether the order should not cross the book.
        """
        super().__init__(api, market)
        self.post_only = post_only

    def create(self, side, amount, price):
        """
        Create a new limit order.
        :param side: 'buy' or 'sell'.
        :param amount: Order amount.
        :param price: Limit price.
        """
        try:
            self.side = side
            self.amount = amount
            self.price = self.api.round_price(price)

            # Check post-only constraint
            if self.post_only:
                if side == "buy" and self.price > self.api.get_ticker()["ask"]:
                    raise ValueError("Limit order crosses the book on a buy.")
                if side == "sell" and self.price < self.api.get_ticker()["bid"]:
                    raise ValueError("Limit order crosses the book on a sell.")

            logging.info(f"Creating {side} limit order: {amount} at {price}")
            self.submit(side, amount, self.price)
        except Exception as e:
            self.state = OrderStates.ERROR
            logging.error(f"Error creating limit order: {e}")
            raise

    def move_price(self, new_price):
        """
        Modify the price of an open limit order.
        :param new_price: The new limit price.
        """
        try:
            if self.completed:
                logging.warning("Cannot move price of a completed order.")
                return

            if self.state in [OrderStates.SUBMITTED, OrderStates.MOVING, OrderStates.CHECKING]:
                logging.info("Order is in transition. Queuing price move.")
                self.moving_price = new_price
                return

            # Cancel and recreate the order with a new price
            self.cancel()
            self.create(self.side, self.amount, new_price)
            logging.info(f"Order price moved to {new_price}.")
        except Exception as e:
            self.state = OrderStates.ERROR
            logging.error(f"Error moving limit order price: {e}")
            raise

    def move_amount(self, new_amount):
        """
        Modify the amount of an open limit order.
        :param new_amount: The new order amount.
        """
        try:
            if self.completed:
                logging.warning("Cannot move amount of a completed order.")
                return

            if self.state in [OrderStates.SUBMITTED, OrderStates.MOVING, OrderStates.CHECKING]:
                logging.info("Order is in transition. Queuing amount move.")
                self.moving_amount = new_amount
                return

            # Cancel and recreate the order with a new amount
            self.cancel()
            self.create(self.side, new_amount, self.price)
            logging.info(f"Order amount moved to {new_amount}.")
        except Exception as e:
            self.state = OrderStates.ERROR
            logging.error(f"Error moving limit order amount: {e}")
            raise
