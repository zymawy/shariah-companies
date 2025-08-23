"""
Logging utility for the scraper
"""
from loguru import logger
import sys
from pathlib import Path
import config

# Configure logger
logger.remove()  # Remove default handler

# Add console handler
logger.add(
    sys.stdout,
    format=config.LOG_FORMAT,
    level=config.LOG_LEVEL,
    colorize=True
)

# Add file handler
log_file = config.LOGS_DIR / "scraper.log"
logger.add(
    log_file,
    format=config.LOG_FORMAT,
    level=config.LOG_LEVEL,
    rotation="1 day",
    retention="7 days",
    compression="zip"
)

def get_logger():
    """Get configured logger instance"""
    return logger