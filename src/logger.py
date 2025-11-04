"""
Logging utilities for the Dynamic Analysis Agent.
"""

import logging
import logging.handlers
import sys
from .config import config

def setup_logging():
    """Setup logging configuration based on config."""
    logger = logging.getLogger('dynamic_analysis_agent')
    logger.setLevel(getattr(logging, config.get('logging.level', 'INFO')))

    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler with rotation
    if config.get('logging.file'):
        file_handler = logging.handlers.RotatingFileHandler(
            config.get('logging.file'),
            maxBytes=config.get('logging.max_file_size', 10485760),
            backupCount=config.get('logging.backup_count', 5)
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

def reload_logger():
    """Reload logger configuration (useful when config changes)."""
    global logger
    logger = setup_logging()
    return logger

# Global logger instance
logger = setup_logging()
