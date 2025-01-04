import logging
from src.orders.base_order import BaseOrder, OrderStates


class StickyOrder(BaseOrder):
    """Class for managing sticky orders."""

    def __init__(self, api, market, outbid=True):
        """
        Initialize the StickyOrder.
        :param api: API instance for exchange interactions.
        :param market: Market information.
        :param outbid: Whether to outbid the current best price.
        """
        super().__init__(api, market)
        self.outbid = outbid
        self.limit = None
        self.ticker = None

    def create(self, side, amount, params=None):
        """
        Create a sticky order.
        :param side: 'buy' or 'sell'.
        :param amount: Order amount.
        :param params: Additional parameters (e.g., limit price).
        """
        try:
            self.side = side
            self.amount = self.api.round_amount(amount)
            self.limit = params.get("limit") if params else None

            self.fetch_ticker()
            self.price = self.calculate_price()

            logging.info(f"Creating sticky {side} order: {amount} at {self.price}")
            self.submit(side, self.amount, self.price)
        except Exception as e:
            self.state = OrderStates.ERROR
            logging.error(f"Error creating sticky order: {e}")
            raise

    def fetch_ticker(self):
        """Fetch the latest ticker data."""
        try:
            self.ticker = self.api.get_ticker()
        except Exception as e:
            logging.error(f"Error fetching ticker: {e}")
            raise

    def calculate_price(self):
        """
        Calculate the sticky order price based on the current ticker and limit.
        :return: Calculated price.
        """
        try:
            if self.side == "buy":
                if self.limit and self.ticker["bid"] >= self.limit:
                    return self.api.round_price(self.limit)
                if self.outbid:
                    return self.api.round_price(self.ticker["bid"] + self.api.get_tick_size())
                return self.api.round_price(self.ticker["bid"])
            elif self.side == "sell":
                if self.limit and self.ticker["ask"] <= self.limit:
                    return self.api.round_price(self.limit)
                if self.outbid:
                    return self.api.round_price(self.ticker["ask"] - self.api.get_tick_size())
                return self.api.round_price(self.ticker["ask"])
        except Exception as e:
            logging.error(f"Error calculating sticky order price: {e}")
            raise

    def adjust_price(self):
        """
        Adjust the price of the sticky order based on updated market conditions.
        """
        try:
            self.fetch_ticker()
            new_price = self.calculate_price()
            if new_price != self.price:
                logging.info(f"Adjusting sticky order price from {self.price} to {new_price}")
                self.move_price(new_price)
        except Exception as e:
            logging.error(f"Error adjusting sticky order price: {e}")
            raise

    def move_price(self, new_price):
        """
        Move the price of the sticky order to a new value.
        :param new_price: New price to move to.
        """
        if self.completed:
            logging.warning("Cannot move price of a completed order.")
            return

        logging.info(f"Moving sticky order price to {new_price}")
        super().move_price(new_price)
