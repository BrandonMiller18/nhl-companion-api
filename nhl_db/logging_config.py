import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging() -> None:
    """
    Configure application-wide logging for production deployment.
    
    - Logs INFO level and above to console (stdout) for Heroku/cloud platforms
    - Optionally logs to file if LOG_TO_FILE environment variable is set
    - Format includes timestamp, module, level, function name, and message
    """
    # Define log format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Create formatter
    formatter = logging.Formatter(log_format, datefmt=date_format)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # Always create console handler (primary for Heroku)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Optionally add file handler for local development
    if os.getenv("LOG_TO_FILE", "false").lower() == "true":
        current_file = Path(__file__)
        logs_dir = current_file.parent.parent / "logs"
        logs_dir.mkdir(exist_ok=True)
        log_file = logs_dir / "nhl_companion.log"
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the given module name.
    
    Args:
        name: Usually __name__ from the calling module
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)

