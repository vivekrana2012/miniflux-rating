#!/usr/bin/env python3
"""
Logging configuration with automatic file rotation.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_LOG_DIR = os.path.join(SCRIPT_DIR, 'logs')


def setup_logger(name='miniflux_rating', log_dir=None, max_bytes=1024*1024, backup_count=10):
    """
    Configure logger with rotating file handler.
    
    Args:
        name (str): Logger name
        log_dir (str): Directory for log files (default: script_dir/logs)
        max_bytes (int): Max file size before rotation (default: 1MB)
        backup_count (int): Number of backup files to keep
    
    Returns:
        logging.Logger: Configured logger instance
    """
    if log_dir is None:
        log_dir = DEFAULT_LOG_DIR
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Create console handler (always available)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Try to set up file logging
    try:
        # Create logs directory with explicit permissions if it doesn't exist
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, mode=0o755)
        
        # Create rotating file handler (1 MB max, keep 10 backups)
        log_file = os.path.join(log_dir, 'miniflux_rating.log')
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except (PermissionError, OSError) as e:
        logger.warning(f"Could not set up file logging: {e}. Logging to console only.")
    
    return logger


# Create default logger instance
logger = setup_logger()
