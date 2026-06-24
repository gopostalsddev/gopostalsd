"""
Advanced Error Handling System for Go Postal SD Application

This module provides comprehensive error handling, logging, and monitoring capabilities
for production-ready error management.
"""

import logging
import traceback
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Union
from enum import Enum
from flask import request, g, current_app
from werkzeug.exceptions import HTTPException
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration


class ErrorSeverity(Enum):
    """Error severity levels for monitoring and alerting."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for better organization and monitoring."""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    VALIDATION = "validation"
    DATABASE = "database"
    EXTERNAL_API = "external_api"
    BUSINESS_LOGIC = "business_logic"
    SYSTEM = "system"
    SECURITY = "security"
    PERFORMANCE = "performance"


class ApplicationError(Exception):
    """Base application error with enhanced context."""
    
    def __init__(
        self,
        message: str,
        error_code: str = None,
        category: ErrorCategory = ErrorCategory.SYSTEM,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        details: Dict[str, Any] = None,
        user_message: str = None,
        retryable: bool = False,
        status_code: int = 500
    ):
        super().__init__(message)
        self.error_id = str(uuid.uuid4())
        self.timestamp = datetime.now(timezone.utc)
        self.message = message
        self.error_code = error_code or f"ERR_{category.value.upper()}"
        self.category = category
        self.severity = severity
        self.details = details or {}
        self.user_message = user_message or message
        self.retryable = retryable
        self.status_code = status_code
        self.request_id = getattr(g, 'request_id', None)
        self.user_id = getattr(g, 'current_user', {}).get('id') if hasattr(g, 'current_user') else None


class ValidationError(ApplicationError):
    """Validation-specific error."""
    
    def __init__(self, message: str, field: str = None, value: Any = None, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.LOW,
            status_code=400,
            **kwargs
        )
        self.field = field
        self.value = value


class AuthenticationError(ApplicationError):
    """Authentication-specific error."""
    
    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.AUTHENTICATION,
            severity=ErrorSeverity.MEDIUM,
            status_code=401,
            **kwargs
        )


class AuthorizationError(ApplicationError):
    """Authorization-specific error."""
    
    def __init__(self, message: str = "Access denied", **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.AUTHORIZATION,
            severity=ErrorSeverity.MEDIUM,
            status_code=403,
            **kwargs
        )


class ExternalAPIError(ApplicationError):
    """External API error."""
    
    def __init__(self, message: str, service: str = None, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.EXTERNAL_API,
            severity=ErrorSeverity.HIGH,
            retryable=True,
            **kwargs
        )
        self.service = service


class DatabaseError(ApplicationError):
    """Database-specific error."""
    
    def __init__(self, message: str, operation: str = None, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )
        self.operation = operation


class SecurityError(ApplicationError):
    """Security-related error."""
    
    def __init__(self, message: str, threat_level: str = "medium", **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.SECURITY,
            severity=ErrorSeverity.CRITICAL if threat_level == "high" else ErrorSeverity.HIGH,
            status_code=403,
            **kwargs
        )
        self.threat_level = threat_level


class ErrorHandler:
    """Centralized error handling and logging system."""
    
    def __init__(self, app=None):
        self.logger = logging.getLogger(__name__)
        self.error_stats = {}
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize error handling for Flask app."""
        self.app = app
        
        # Configure Sentry for production error tracking
        if app.config.get('SENTRY_DSN'):
            sentry_sdk.init(
                dsn=app.config['SENTRY_DSN'],
                integrations=[
                    FlaskIntegration(),
                    SqlalchemyIntegration(),
                ],
                traces_sample_rate=app.config.get('SENTRY_TRACES_SAMPLE_RATE', 0.1),
                environment=app.config.get('ENVIRONMENT', 'development'),
            )
        
        # Register error handlers
        app.register_error_handler(ApplicationError, self.handle_application_error)
        app.register_error_handler(HTTPException, self.handle_http_error)
        app.register_error_handler(Exception, self.handle_generic_error)
        
        # Register request context processors
        app.before_request(self.before_request)
        app.after_request(self.after_request)
    
    def before_request(self):
        """Set up request context for error tracking."""
        g.request_id = str(uuid.uuid4())
        g.start_time = datetime.now(timezone.utc)
    
    def after_request(self, response):
        """Log request completion and performance metrics."""
        if hasattr(g, 'start_time'):
            duration = (datetime.now(timezone.utc) - g.start_time).total_seconds()
            
            # Log performance metrics
            self.logger.info(
                f"Request completed",
                extra={
                    'request_id': g.request_id,
                    'method': request.method,
                    'path': request.path,
                    'status_code': response.status_code,
                    'duration': duration,
                    'user_agent': request.headers.get('User-Agent'),
                    'ip_address': request.environ.get('REMOTE_ADDR')
                }
            )
            
            # Track slow requests
            if duration > 2.0:  # 2 seconds threshold
                self.logger.warning(
                    f"Slow request detected",
                    extra={
                        'request_id': g.request_id,
                        'duration': duration,
                        'path': request.path
                    }
                )
        
        return response
    
    def handle_application_error(self, error: ApplicationError):
        """Handle custom application errors."""
        return self._create_error_response(error)
    
    def handle_http_error(self, error: HTTPException):
        """Handle HTTP exceptions."""
        app_error = ApplicationError(
            message=error.description or str(error),
            error_code=f"HTTP_{error.code}",
            status_code=error.code,
            severity=ErrorSeverity.LOW if error.code < 500 else ErrorSeverity.MEDIUM
        )
        return self._create_error_response(app_error)
    
    def handle_generic_error(self, error: Exception):
        """Handle unexpected errors."""
        app_error = ApplicationError(
            message="An unexpected error occurred",
            error_code="INTERNAL_ERROR",
            severity=ErrorSeverity.CRITICAL,
            details={
                'exception_type': type(error).__name__,
                'traceback': traceback.format_exc()
            }
        )
        return self._create_error_response(app_error)
    
    def _create_error_response(self, error: ApplicationError):
        """Create standardized error response."""
        # Log the error
        self._log_error(error)
        
        # Track error statistics
        self._track_error_stats(error)
        
        # Send to monitoring service if configured
        self._send_to_monitoring(error)
        
        # Create response
        response_data = {
            'error': {
                'id': error.error_id,
                'code': error.error_code,
                'message': error.user_message,
                'category': error.category.value,
                'severity': error.severity.value,
                'timestamp': error.timestamp.isoformat(),
                'retryable': error.retryable
            }
        }
        
        # Add debug information in development
        if current_app.config.get('DEBUG', False):
            response_data['error']['details'] = error.details
            response_data['error']['request_id'] = error.request_id
        
        return response_data, error.status_code
    
    def _log_error(self, error: ApplicationError):
        """Log error with appropriate level and context."""
        log_data = {
            'error_id': error.error_id,
            'error_code': error.error_code,
            'category': error.category.value,
            'severity': error.severity.value,
            'message': error.message,
            'user_message': error.user_message,
            'request_id': error.request_id,
            'user_id': error.user_id,
            'details': error.details,
            'retryable': error.retryable
        }
        
        # Add request context
        if request:
            log_data.update({
                'method': request.method,
                'path': request.path,
                'ip_address': request.environ.get('REMOTE_ADDR'),
                'user_agent': request.headers.get('User-Agent')
            })
        
        # Log based on severity
        if error.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(f"Critical error: {error.message}", extra=log_data)
        elif error.severity == ErrorSeverity.HIGH:
            self.logger.error(f"High severity error: {error.message}", extra=log_data)
        elif error.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(f"Medium severity error: {error.message}", extra=log_data)
        else:
            self.logger.info(f"Low severity error: {error.message}", extra=log_data)
    
    def _track_error_stats(self, error: ApplicationError):
        """Track error statistics for monitoring."""
        category = error.category.value
        severity = error.severity.value
        
        if category not in self.error_stats:
            self.error_stats[category] = {}
        
        if severity not in self.error_stats[category]:
            self.error_stats[category][severity] = 0
        
        self.error_stats[category][severity] += 1
    
    def _send_to_monitoring(self, error: ApplicationError):
        """Send error to external monitoring service."""
        # Send to Sentry if configured
        if current_app.config.get('SENTRY_DSN'):
            with sentry_sdk.push_scope() as scope:
                scope.set_tag("error_category", error.category.value)
                scope.set_tag("error_severity", error.severity.value)
                scope.set_tag("error_code", error.error_code)
                scope.set_context("error_details", error.details)
                
                if error.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
                    sentry_sdk.capture_exception(error)
                else:
                    sentry_sdk.capture_message(error.message, level="warning")
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get current error statistics."""
        return {
            'stats': self.error_stats,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }


# Global error handler instance
error_handler = ErrorHandler()


def init_error_handling(app):
    """Initialize error handling for the Flask application."""
    error_handler.init_app(app)
    return error_handler


# Convenience functions for common error scenarios
def raise_validation_error(message: str, field: str = None, value: Any = None):
    """Raise a validation error."""
    raise ValidationError(message, field=field, value=value)


def raise_auth_error(message: str = "Authentication failed"):
    """Raise an authentication error."""
    raise AuthenticationError(message)


def raise_authz_error(message: str = "Access denied"):
    """Raise an authorization error."""
    raise AuthorizationError(message)


def raise_external_api_error(message: str, service: str = None):
    """Raise an external API error."""
    raise ExternalAPIError(message, service=service)


def raise_database_error(message: str, operation: str = None):
    """Raise a database error."""
    raise DatabaseError(message, operation=operation)


def raise_security_error(message: str, threat_level: str = "medium"):
    """Raise a security error."""
    raise SecurityError(message, threat_level=threat_level)
