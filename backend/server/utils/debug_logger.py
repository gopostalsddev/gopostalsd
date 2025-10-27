"""
Debug Logger Utility for Go Postal SD

Provides development-only logging utilities that automatically
handle sensitive information masking and environment detection.
"""

import os
import logging
from functools import wraps
from typing import Any, Callable, Dict

# Check if we're in development mode
IS_DEVELOPMENT = os.getenv('ENVIRONMENT', 'development') in ['development', 'testing']

# Create a development logger
dev_logger = logging.getLogger('dev_debug')

# Dictionary to track what to mask
SENSITIVE_KEYS = {'password', 'password_hash', 'session_token', 'refresh_token', 
                  'api_key', 'secret', 'token', 'credit_card', 'ssn', 'social_security'}


def sanitize_data(data: Any) -> Any:
    """
    Recursively sanitize data by masking sensitive fields.
    
    Args:
        data: Data to sanitize
        
    Returns:
        Sanitized data
    """
    if isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            # Check if key is sensitive
            if any(sensitive_key in key.lower() for sensitive_key in SENSITIVE_KEYS):
                sanitized[key] = '***MASKED***'
            else:
                sanitized[key] = sanitize_data(value)
        return sanitized
    elif isinstance(data, list):
        return [sanitize_data(item) for item in data]
    elif isinstance(data, str) and len(data) > 100:
        # Truncate very long strings
        return data[:100] + '...(truncated)'
    else:
        return data


def log_request(function_name: str, **kwargs):
    """
    Log a request with sanitized parameters.
    
    Args:
        function_name: Name of the function being called
        **kwargs: Parameters to log
    """
    if IS_DEVELOPMENT:
        sanitized = sanitize_data(kwargs)
        dev_logger.info(f"🔵 {function_name}() - Request: {sanitized}")


def log_response(function_name: str, result: Any):
    """
    Log a response with sanitized data.
    
    Args:
        function_name: Name of the function
        result: Result to log
    """
    if IS_DEVELOPMENT:
        sanitized = sanitize_data(result)
        dev_logger.info(f"✅ {function_name}() - Response: {sanitized}")


def log_error(function_name: str, error: Exception):
    """
    Log an error.
    
    Args:
        function_name: Name of the function
        error: Exception that occurred
    """
    if IS_DEVELOPMENT:
        dev_logger.error(f"❌ {function_name}() - Error: {str(error)}", exc_info=True)


def debug_log(func: Callable) -> Callable:
    """
    Decorator to automatically log function calls and responses in development.
    
    Usage:
        @debug_log
        def my_function(param1, param2):
            return result
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if IS_DEVELOPMENT:
            # Log function entry
            log_request(func.__name__, args=args, kwargs=kwargs)
        
        try:
            result = func(*args, **kwargs)
            
            if IS_DEVELOPMENT:
                # Log successful result
                log_response(func.__name__, result)
            
            return result
        except Exception as e:
            if IS_DEVELOPMENT:
                # Log error
                log_error(func.__name__, e)
            raise
    
    return wrapper


def log_api_request(method: str, path: str, data: Dict = None, headers: Dict = None):
    """
    Log an API request.
    
    Args:
        method: HTTP method
        path: Request path
        data: Request data
        headers: Request headers
    """
    if IS_DEVELOPMENT:
        sanitized_data = sanitize_data(data) if data else None
        sanitized_headers = sanitize_data(headers) if headers else None
        dev_logger.info(f"🌐 API Request: {method} {path}")
        if sanitized_data:
            dev_logger.info(f"   Data: {sanitized_data}")
        if sanitized_headers:
            dev_logger.info(f"   Headers: {sanitized_headers}")


def log_api_response(path: str, status_code: int, data: Any = None):
    """
    Log an API response.
    
    Args:
        path: Request path
        status_code: HTTP status code
        data: Response data
    """
    if IS_DEVELOPMENT:
        emoji = "✅" if 200 <= status_code < 300 else "❌" if status_code >= 400 else "⚠️"
        sanitized_data = sanitize_data(data) if data else None
        dev_logger.info(f"{emoji} API Response: {status_code} {path}")
        if sanitized_data:
            dev_logger.info(f"   Data: {sanitized_data}")

