import logging
from logging.handlers import RotatingFileHandler


def setup_logger():
    """
    Configures the global logger for the application.
    Writes logs to 'smartcredit.log' with rotation (max 1MB, 3 backups).
    """
    log_file = "smartcredit.log"

    # Create logger
    logger = logging.getLogger("SmartCredit")
    logger.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # File Handler (Rolling)
    file_handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024, backupCount=3)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # Console Handler (Optional, for dev)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)

    # Add handlers
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    logger.info("Logger initialized successfully.")
    return logger
