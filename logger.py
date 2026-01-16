"""
VARIOSYNC Logging Module
Handles logging configuration and setup for the application.
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


class VariosyncLogger:
    """Centralized logging configuration for VARIOSYNC."""
    
    _logger: Optional[logging.Logger] = None
    _initialized: bool = False
    
    @classmethod
    def setup_logger(
        cls,
        log_level: str = "INFO",
        log_format: Optional[str] = None,
        log_file: Optional[str] = None,
        enable_console: bool = True
    ) -> logging.Logger:
        """
        Setup and configure the application logger.
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_format: Custom log format string
            log_file: Path to log file (optional)
            enable_console: Enable console logging
            
        Returns:
            Configured logger instance
        """
        if cls._initialized and cls._logger:
            return cls._logger
        
        # Create logger
        logger = logging.getLogger("variosync")
        logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        
        # Prevent duplicate handlers
        if logger.handlers:
            return logger
        
        # Default format
        if log_format is None:
            log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        
        formatter = logging.Formatter(log_format)
        
        # Console handler
        if enable_console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        # File handler
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        cls._logger = logger
        cls._initialized = True
        
        return logger
    
    @classmethod
    def get_logger(cls) -> logging.Logger:
        """
        Get the configured logger instance.
        
        Returns:
            Logger instance
        """
        if cls._logger is None:
            # Setup with defaults from environment
            log_level = os.getenv("LOG_LEVEL", "INFO")
            log_file = os.getenv("LOG_FILE", "variosync.log")
            return cls.setup_logger(log_level=log_level, log_file=log_file)
        
        return cls._logger
    
    @classmethod
    def reset(cls) -> None:
        """Reset logger state (useful for testing)."""
        cls._logger = None
        cls._initialized = False


def get_logger() -> logging.Logger:
    """
    Convenience function to get the logger instance.
    
    Returns:
        Logger instance
    """
    return VariosyncLogger.get_logger()
