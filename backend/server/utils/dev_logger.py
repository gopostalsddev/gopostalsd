"""
Development Logger for Go Postal SD

Provides centralized logging for development environment only.
All logs are automatically filtered in production.
"""

import os
import logging
from functools import wraps
from typing import Any, Dict

# Check if we're in development mode
IS_DEVELOPMENT = os.getenv('ENVIRONMENT', 'development') in ['development', 'testing']

# Create dev logger
dev_logger = logging.getLogger('dev')


def log_function_call(func_name: str, **kwargs):
    """Log a function call with parameters."""
    if IS_DEVELOPMENT:
        sanitized = _sanitize_data(kwargs)
        dev_logger.info(f"CALL: {func_name}({sanitized})")


def log_function_result(func_name: str, result: Any):
    """Log a function result."""
    if IS_DEVELOPMENT:
        sanitized = _sanitize_data(result)
        dev_logger.info(f"RESULT: {func_name} -> {sanitized}")


def log_function_error(func_name: str, error: Exception):
    """Log a function error."""
    if IS_DEVELOPMENT:
        dev_logger.error(f"ERROR: {func_name} - {type(error).__name__}: {str(error)}", exc_info=True)


def log_service_call(service_name: str, method: str, **kwargs):
    """Log a service method call."""
    if IS_DEVELOPMENT:
        sanitized = _sanitize_data(kwargs)
        dev_logger.info(f"SERVICE: {service_name}.{method}({sanitized})")


def log_service_result(service_name: str, method: str, result: Any):
    """Log a service method result."""
    if IS_DEVELOPMENT:
        sanitized = _sanitize_data(result)
        dev_logger.info(f"SERVICE RESULT: {service_name}.{method} -> {sanitized}")


def log_api_route(method: str, route: str, data: Dict = None):
    """Log an API route call."""
    if IS_DEVELOPMENT:
        sanitized = _sanitize_data(data) if data else None
        dev_logger.info(f"API: {method} {route}")
        if sanitized:
            dev_logger.info(f"  Data: {sanitized}")


def log_api_response(route: str, status_code: int, data: Any = None):
    """Log an API response."""
    if IS_DEVELOPMENT:
        emoji = _get_emoji_for_status(status_code)
        dev_logger.info(f"{emoji} API: {status_code} {route}")
        if data and status_code >= 400:
            sanitized = _sanitize_data(data)
            dev_logger.info(f"  Error: {sanitized}")


def _get_emoji_for_status(status_code: int) -> str:
    """Get emoji for HTTP status code."""
    if 200 <= status_code < 300:
        return "✅"
    elif 400 <= status_code < 500:
        return "❌"
    elif status_code >= 500:
        return "💥"
    else:
        return "⚠️"


def _sanitize_data(data: Any) -> Any:
    """
    Recursively sanitize data by masking sensitive fields.
    
    Args:
        data: Data to sanitize
        
    Returns:
        Sanitized data
    """
    sensitive_keys = {'password', 'password_hash', 'session_token', 'refresh_token', 
                      'api_key', 'secret', 'token', 'credit_card', 'ssn'}
    
    if isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            # Check if key is sensitive
            if any(sensitive_key in key.lower() for sensitive_key in sensitive_keys):
                sanitized[key] = '***MASKED***'
            else:
                sanitized[key] = _sanitize_data(value)
        return sanitized
    elif isinstance(data, list):
        return [_sanitize_data(item) for item in data]
    elif isinstance(data, str) and len(data) > 200:
        # Truncate very long strings
        return data[:200] + '...(truncated)'
    else:
        return data


def dev_log(f):
    """
    Decorator to automatically log function calls in development.
    
    Usage:
        @dev_log
        def my_function(param1, param2):
            return result
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        if IS_DEVELOPMENT:
            log_function_call(f.__name__, args=args, kwargs=kwargs)
        
        try:
            result = f(*args, **kwargs)
            
            if IS_DEVELOPMENT:
                log_function_result(f.__name__, result)
            
            return result
        except Exception as e:
            if IS_DEVELOPMENT:
                log_function_error(f.__name__, e)
            raise
    
    return wrapper

