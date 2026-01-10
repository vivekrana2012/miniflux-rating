#!/usr/bin/env python3
"""
Logging configuration with automatic file rotation.
"""

import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logger(name='miniflux_rating', log_dir='logs', max_bytes=1024*1024, backup_count=10):
    """
    Configure logger with rotating file handler.
    
    Args:
        name (str): Logger name
        log_dir (str): Directory for log files
        max_bytes (int): Max file size before rotation (default: 1MB)
        backup_count (int): Number of backup files to keep
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Create rotating file handler (1 MB max, keep 10 backups)
    log_file = os.path.join(log_dir, 'miniflux_rating.log')
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# Create default logger instance
logger = setup_logger()
