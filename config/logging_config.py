import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging(log_dir="data/logs", log_file="bot_logs.txt", error_file="errors.log"):
    """
    Sets up centralized logging for the trading bot.
    :param log_dir: Directory to store log files.
    :param log_file: File name for general logs.
    :param error_file: File name for error logs.
    """
    # Ensure log directory exists
    os.makedirs(log_dir, exist_ok=True)

    # General log file configuration
    general_handler = RotatingFileHandler(
        os.path.join(log_dir, log_file), maxBytes=5 * 1024 * 1024, backupCount=3
    )
    general_handler.setLevel(logging.INFO)
    general_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    general_handler.setFormatter(general_formatter)

    # Error log file configuration
    error_handler = RotatingFileHandler(
        os.path.join(log_dir, error_file), maxBytes=5 * 1024 * 1024, backupCount=3
    )
    error_handler.setLevel(logging.ERROR)
    error_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    error_handler.setFormatter(error_formatter)

    # Console log configuration
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(console_formatter)

    # Root logger configuration
    logging.basicConfig(level=logging.INFO, handlers=[general_handler, error_handler, console_handler])

    logging.info("Logging initialized.")
