import time
import logging

class ExchangeUtils:
    @staticmethod
    def retry(api_call, retries=5, delay=2, backoff=2):
        """
        Retry a function in case of failure.

        :param api_call: The API call to retry.
        :param retries: Number of retries.
        :param delay: Initial delay between retries.
        :param backoff: Backoff multiplier for delays.
        :return: Result of the API call or raises an exception after retries.
        """
        attempt = 0
        while attempt < retries:
            try:
                return api_call()
            except Exception as e:
                attempt += 1
                logging.warning(f"Attempt {attempt}/{retries} failed: {e}")
                if attempt < retries:
                    time.sleep(delay)
                    delay *= backoff
                else:
                    logging.error("Max retries reached. Raising exception.")
                    raise

    @staticmethod
    def is_valid_order(market, amount, price=None):
        """
        Validate if an order is valid based on market restrictions.

        :param market: Market configuration (e.g., minimal order amount, price).
        :param amount: Order amount.
        :param price: Order price (optional).
        :return: A dictionary with `valid` (bool) and `reason` (str).
        """
        if amount < market.get("minimalOrder", {}).get("amount", 0):
            return {"valid": False, "reason": "Amount is too small"}

        if price:
            if "isValidPrice" in market and not market["isValidPrice"](price):
                return {"valid": False, "reason": "Price is not valid"}

        return {"valid": True, "reason": ""}

    @staticmethod
    def bind_all(target_instance, method_names=None):
        """
        Binds all methods of a class to the instance.

        :param target_instance: The class instance.
        :param method_names: Optional list of method names to bind. Binds all if None.
        """
        methods = (
            method_names
            if method_names
            else [method for method in dir(target_instance) if callable(getattr(target_instance, method))]
        )
        for method_name in methods:
            method = getattr(target_instance, method_name)
            setattr(target_instance, method_name, method.__get__(target_instance, target_instance.__class__))
