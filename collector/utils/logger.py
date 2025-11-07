import logging
import os
from logging.handlers import RotatingFileHandler

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_DIR = os.getenv("LOG_DIR", "/var/log/renova")
LOG_FILE = os.path.join(LOG_DIR, "collector.log")

os.makedirs(LOG_DIR, exist_ok=True)

formatter = logging.Formatter(
    fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

file_handler = RotatingFileHandler(
    LOG_FILE, maxBytes=5_000_000, backupCount=3, encoding="utf-8"
)
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

logging.basicConfig(
    level=LOG_LEVEL,
    handlers=[file_handler, console_handler],
)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
