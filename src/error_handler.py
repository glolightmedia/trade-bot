import logging
import traceback

class ErrorHandler:
    """
    Centralized error handling for the trading bot.
    Logs errors and provides detailed tracebacks for debugging.
    """

    @staticmethod
    def log_error(module_name, error_message):
        """
        Logs an error message with traceback details.
        :param module_name: Name of the module where the error occurred.
        :param error_message: The error message to log.
        """
        logger = logging.getLogger(module_name)
        logger.error(f"Error in {module_name}: {error_message}")
        logger.error(traceback.format_exc())

    @staticmethod
    def handle_critical_error(module_name, error_message, notify_admin=False):
        """
        Handles critical errors and optionally sends notifications.
        :param module_name: Name of the module where the error occurred.
        :param error_message: The error message to handle.
        :param notify_admin: If True, notify admin about the error.
        """
        ErrorHandler.log_error(module_name, error_message)
        if notify_admin:
            ErrorHandler.notify_admin(error_message)

    @staticmethod
    def notify_admin(error_message):
        """
        Sends a notification to the administrator about a critical error.
        :param error_message: The error message to send.
        """
        # Placeholder for notification logic (e.g., email, SMS, webhook)
        logging.info(f"Admin notified about critical error: {error_message}")
