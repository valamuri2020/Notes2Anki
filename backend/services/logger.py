import logging
import json
import sys
from typing import Any, Dict
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter that structures logs in a Datadog-friendly format."""
    
    def format(self, record: logging.LogRecord) -> str:
        # Base log record attributes
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        # Add extra fields from the record
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)
            
        return json.dumps(log_data)


def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    Set up a logger with the given name and level.
    
    Args:
        name: The name of the logger
        level: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Console handler with JSON formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JSONFormatter())
    logger.addHandler(console_handler)
    
    return logger


# Create the main application logger
app_logger = setup_logger("notes2anki")


class LoggerMixin:
    """Mixin to add logging capabilities to any class."""
    
    def __init__(self):
        self.logger = setup_logger(self.__class__.__name__)
        
    def log_with_context(self, level: str, message: str, **kwargs):
        """
        Log a message with additional context.
        
        Args:
            level: The log level (debug, info, warning, error, critical)
            message: The log message
            **kwargs: Additional context to include in the log
        """
        log_method = getattr(self.logger, level.lower())
        extra = {"extra_fields": kwargs}
        log_method(message, extra=extra) 