import logging
import os

# Logger name
LOG_NAME = os.getenv("APP_LOGGER_NAME", "intaker_data_importer")

# Create base logger
logger = logging.getLogger(LOG_NAME)
logger.setLevel(logging.DEBUG)

# Log format with ISO-like timestamp including milliseconds
LOG_FORMAT = "%(asctime)s.%(msecs)03d - %(filename)s - %(funcName)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"

# Formatter
formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)

# Prevent duplicate handlers
if not logger.handlers:
    logger.addHandler(console_handler)

# Optional file handler
LOG_TO_FILE = os.getenv("LOG_TO_FILE", "false").lower() in ("1", "true", "yes")
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "app.log")

# In AWS Lambda, /var/task is read-only → use /tmp
if LOG_TO_FILE:
    if os.getenv("AWS_LAMBDA_FUNCTION_NAME") and not LOG_FILE_PATH.startswith("/tmp/"):
        LOG_FILE_PATH = "/tmp/app.log"
    try:
        file_handler = logging.FileHandler(LOG_FILE_PATH)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"File logging disabled due to error opening {LOG_FILE_PATH}: {e}")

# Avoid duplicate logs from root logger
logger.propagate = False


def get_logger(name: str):
    """
    Return child logger for a module.
    Usage: logger = get_logger(__name__)
    """
    return logger.getChild(name)
