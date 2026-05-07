"""Enhanced logging configuration for Krishi Saarthi."""
import os
import logging
import sys
from typing import Optional
from datetime import datetime
import json


class KrishiLogger:
    """Enhanced logger with structured logging and correlation IDs."""
    
    def __init__(self, name: str, level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # Console handler with formatting
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler for structured logs
        if os.getenv("LOG_FILE"):
            file_handler = logging.FileHandler(os.getenv("LOG_FILE"))
            file_handler.setFormatter(JsonFormatter())
            self.logger.addHandler(file_handler)
    
    def info(self, message: str, **kwargs):
        """Log info message with optional context."""
        self.logger.info(message, extra=kwargs)
    
    def error(self, message: str, error: Optional[Exception] = None, **kwargs):
        """Log error message with optional exception."""
        if error:
            kwargs['error_type'] = type(error).__name__
            kwargs['error_message'] = str(error)
        self.logger.error(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with optional context."""
        self.logger.warning(message, extra=kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with optional context."""
        self.logger.debug(message, extra=kwargs)
    
    def api_call(self, endpoint: str, method: str, user_id: Optional[int] = None, **kwargs):
        """Log API call with context."""
        self.info(
            f"API call: {method} {endpoint}",
            endpoint=endpoint,
            method=method,
            user_id=user_id,
            **kwargs
        )
    
    def business_event(self, event: str, user_id: Optional[int] = None, **kwargs):
        """Log business event with context."""
        self.info(
            f"Business event: {event}",
            event=event,
            user_id=user_id,
            **kwargs
        )


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }
        
        # Add extra fields
        if hasattr(record, '__dict__'):
            for key, value in record.__dict__.items():
                if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                              'filename', 'module', 'lineno', 'funcName', 'created', 
                              'msecs', 'relativeCreated', 'thread', 'threadName', 
                              'processName', 'process']:
                    log_entry[key] = value
        
        return json.dumps(log_entry)


# Global logger instances
app_logger = KrishiLogger("krishi_app", os.getenv("LOG_LEVEL", "INFO"))
auth_logger = KrishiLogger("krishi_auth", os.getenv("LOG_LEVEL", "INFO"))
db_logger = KrishiLogger("krishi_db", os.getenv("LOG_LEVEL", "INFO"))
llm_logger = KrishiLogger("krishi_llm", os.getenv("LOG_LEVEL", "INFO"))
