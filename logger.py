import os
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

DEFAULT_LOG_PATH = os.path.expanduser("~/logs/prayer.log")

def get_logger(name: str, log_file: str = None) -> logging.Logger:
    if log_file is None:
        log_file = os.getenv("LOG", DEFAULT_LOG_PATH)

    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    file_handler = TimedRotatingFileHandler(
        log_file,
        when="midnight",
        interval=7,
        backupCount=7
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger