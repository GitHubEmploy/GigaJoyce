import logging
import os

def setup_logging(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Set up logging with the specified name and level.

    Args:
        name (str): The name of the logger.
        level (int): The logging level (e.g., logging.INFO, logging.DEBUG).

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Ensure the logs directory exists
    os.makedirs("logs", exist_ok=True)

    # File handler
    file_handler = logging.FileHandler(f"logs/{name}.log", encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(file_handler)

    # Stream handler
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level)
    stream_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
    logger.addHandler(stream_handler)

    return logger
