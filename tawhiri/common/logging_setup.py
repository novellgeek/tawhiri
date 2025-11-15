"""
Logging Configuration

Centralized logging setup for all TAWHIRI modules.
Supports both file and console logging with configurable levels.
"""

import logging
import logging.handlers
import os
from typing import Optional


def setup_logging(
    log_file: Optional[str] = None,
    log_level: str = "INFO",
    log_to_console: bool = True,
    log_format: Optional[str] = None,
) -> logging.Logger:
    """
    Configure logging for TAWHIRI platform.
    
    Args:
        log_file: Path to log file. If None, only console logging is used.
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_console: Whether to also log to console
        log_format: Custom log format string
        
    Returns:
        Root logger instance
        
    Example:
        >>> logger = setup_logging("/var/log/tawhiri/app.log", "INFO")
        >>> logger.info("Application started")
    """
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Default format if none provided
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        try:
            # Create log directory if it doesn't exist
            log_dir = os.path.dirname(log_file)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)
            
            # Use rotating file handler to prevent huge log files
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,  # 10 MB
                backupCount=5,
            )
            file_handler.setLevel(numeric_level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
            
            root_logger.info(f"Logging to file: {log_file}")
            
        except Exception as e:
            root_logger.error(f"Failed to setup file logging: {e}")
    
    return root_logger


def get_module_logger(module_name: str) -> logging.Logger:
    """
    Get a logger for a specific module.
    
    Args:
        module_name: Name of the module (typically __name__)
        
    Returns:
        Logger instance for the module
        
    Example:
        >>> logger = get_module_logger(__name__)
        >>> logger.debug("Debug message from my module")
    """
    return logging.getLogger(module_name)
