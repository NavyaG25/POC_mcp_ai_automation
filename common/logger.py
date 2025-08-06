"""
Logger configuration for the automation framework.
Provides structured logging with file and console outputs.
"""
import logging
import os
import sys
from datetime import datetime
from typing import Optional

class Logger:
    """Centralized logging configuration for the automation framework."""
    
    _logger_initialized = False
    
    @classmethod
    def setup_logger(cls, name: str = 'automation_framework', level: int = logging.INFO) -> logging.Logger:
        """Setup and configure logger with file and console handlers."""
        
        if cls._logger_initialized:
            return logging.getLogger(name)
        
        # Create logs directory if it doesn't exist
        logs_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        # Create logger
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # File handler for all logs
        log_file = os.path.join(logs_dir, f'automation_{datetime.now().strftime("%Y%m%d")}.log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
        
        # File handler for API responses
        api_log_file = os.path.join(logs_dir, f'api_responses_{datetime.now().strftime("%Y%m%d")}.log')
        api_handler = logging.FileHandler(api_log_file, encoding='utf-8')
        api_handler.setLevel(logging.INFO)
        api_handler.setFormatter(detailed_formatter)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        logger.addHandler(console_handler)
        
        # Store API handler as class attribute for direct access
        cls.api_handler = api_handler
        
        cls._logger_initialized = True
        logger.info("Logger initialized successfully")
        
        return logger
    
    @classmethod
    def get_logger(cls, name: str = 'automation_framework') -> logging.Logger:
        """Get configured logger instance."""
        if not cls._logger_initialized:
            return cls.setup_logger(name)
        return logging.getLogger(name)
    
    @classmethod
    def log_api_response(cls, method: str, url: str, status_code: int, 
                        request_data: Optional[dict] = None, 
                        response_data: Optional[dict] = None,
                        correlation_id: Optional[str] = None):
        """Log API request/response with structured format."""
        logger = cls.get_logger()
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'correlation_id': correlation_id or f"api_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'method': method,
            'url': url,
            'status_code': status_code,
            'request_data': request_data,
            'response_data': response_data
        }
        
        logger.info(f"API_CALL: {log_entry}")
        
        # Also log to dedicated API file
        if hasattr(cls, 'api_handler'):
            api_logger = logging.getLogger('api_responses')
            api_logger.addHandler(cls.api_handler)
            api_logger.info(f"API_CALL: {log_entry}")
