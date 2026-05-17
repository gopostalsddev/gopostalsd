"""
Middleware package for Go Postal SD Application

This package contains middleware components for authentication, logging, and other cross-cutting concerns.
"""

from .auth_middleware import (
    require_auth, require_permission, require_role, optional_auth,
    get_current_user, get_current_session_token, is_authenticated,
    has_permission, has_role, is_admin, is_customer,
    get_user_id, get_user_email, get_user_role
)

__all__ = [
    'require_auth', 'require_permission', 'require_role', 'optional_auth',
    'get_current_user', 'get_current_session_token', 'is_authenticated',
    'has_permission', 'has_role', 'is_admin', 'is_customer',
    'get_user_id', 'get_user_email', 'get_user_role'
]
