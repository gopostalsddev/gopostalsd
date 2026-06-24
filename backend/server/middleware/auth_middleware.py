"""
Authentication Middleware for Go Postal SD Application

This module provides authentication middleware for protecting routes and managing user sessions.
"""

import logging
import os
from functools import wraps
from flask import request, g, current_app
from server.models.auth import User, UserSession
from server.services.auth_service import AuthService

logger = logging.getLogger(__name__)

# Module load logging
IS_DEVELOPMENT = os.getenv('ENVIRONMENT', 'development') in ['development', 'testing']
if IS_DEVELOPMENT:
    logger.debug("[AUTH_MIDDLEWARE] Module loaded")


def _extract_session_token() -> str:
    """Extract session token from Authorization header only."""
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header[7:]
    return ''


def enforce_csrf_protection() -> None:
    """Enforce CSRF protection for authenticated state-changing API requests."""
    if request.method not in {'POST', 'PUT', 'PATCH', 'DELETE'}:
        return

    if not request.path.startswith('/api/'):
        return

    session_token = _extract_session_token()
    if not session_token:
        return

    csrf_header = request.headers.get('X-CSRF-Token')
    if not csrf_header or csrf_header != session_token:
        from flask import abort
        logger.warning("Blocked request with missing or invalid CSRF token for path %s", request.path)
        abort(403, description='Missing or invalid CSRF token')


def require_cart_auth(f):
    """
    Decorator to allow authenticated users or fall back to cart session.
    For cart operations, we don't need full authentication - just verify user exists if session token provided.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logger.debug(f"Cart auth check for {request.method} {request.path}")
        
        try:
            # Get session token from Authorization header or query parameter
            session_token = _extract_session_token()
            
            if IS_DEVELOPMENT:
                logger.debug("[CART AUTH] Session token found: %s", session_token is not None)
            
            # For cart operations, if we have a session token, try to verify it
            # If it fails, we'll just proceed without user context (guest cart)
            if session_token:
                try:
                    from flask import current_app
                    auth_service = current_app.extensions.get('auth_service')
                    if auth_service:
                        user = auth_service.get_user_by_session(session_token)
                        if user:
                            if IS_DEVELOPMENT:
                                logger.debug("[CART AUTH] User authenticated: %s", user.email)
                            logger.debug(f"Authenticated user for cart: {user.email}")
                            # Set user context for authenticated users
                            g.current_user = user
                            request.user_id = user.id
                        else:
                            logger.debug("No user found for cart session token")
                except Exception as e:
                    logger.debug(f"Could not verify cart session: {str(e)}", exc_info=True)
                    # Continue without user context
            
            return f(*args, **kwargs)
        except Exception as e:
            logger.exception("Cart auth decorator encountered an error: %s", str(e))
            raise
    
    return decorated_function


def require_auth(f):
    """
    Decorator to require authentication for a route.
    
    Usage:
        @require_auth
        def protected_route():
            # Access current user via g.current_user
            pass
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_token = _extract_session_token()
        
        if not session_token:
            return {'error': 'Authentication required', 'code': 'AUTH_REQUIRED'}, 401
        
        # Get auth service
        auth_service = current_app.extensions.get('auth_service')
        if not auth_service:
            logger.error("Auth service not available")
            return {'error': 'Authentication service unavailable', 'code': 'SERVICE_UNAVAILABLE'}, 500
        
        # Get user by session
        user = auth_service.get_user_by_session(session_token)
        if not user:
            return {'error': 'Invalid or expired session', 'code': 'INVALID_SESSION'}, 401
        
        # Check if user is active
        if not user.is_active():
            return {'error': 'Account is not active', 'code': 'ACCOUNT_INACTIVE'}, 401
        
        # Store user in g for access in route
        g.current_user = user
        g.session_token = session_token
        request.user_id = user.id
        
        return f(*args, **kwargs)
    
    return decorated_function


def require_permission(permission: str):
    """
    Decorator to require specific permission for a route.
    
    Args:
        permission: Required permission name
        
    Usage:
        @require_permission('users.read')
        def get_users():
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # First check if user is authenticated
            if not hasattr(g, 'current_user') or not g.current_user:
                return {'error': 'Authentication required', 'code': 'AUTH_REQUIRED'}, 401
            
            # Check if user has required permission
            if not g.current_user.role.has_permission(permission):
                return {'error': 'Insufficient permissions', 'code': 'INSUFFICIENT_PERMISSIONS'}, 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def require_role(role_name: str):
    """
    Decorator to require specific role for a route.
    
    Args:
        role_name: Required role name
        
    Usage:
        @require_role('Admin')
        def admin_only_route():
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Ensure authenticated user context exists for role-protected routes.
            # Some endpoints only use @require_role without @require_auth.
            user = getattr(g, 'current_user', None)
            if not user:
                session_token = None
                session_token = _extract_session_token()

                if not session_token:
                    return {'error': 'Authentication required', 'code': 'AUTH_REQUIRED'}, 401

                auth_service = current_app.extensions.get('auth_service')
                if not auth_service:
                    logger.error("Auth service not available")
                    return {'error': 'Authentication service unavailable', 'code': 'SERVICE_UNAVAILABLE'}, 500

                user = auth_service.get_user_by_session(session_token)
                if not user:
                    return {'error': 'Invalid or expired session', 'code': 'INVALID_SESSION'}, 401

                if not user.is_active():
                    return {'error': 'Account is not active', 'code': 'ACCOUNT_INACTIVE'}, 401

                g.current_user = user
                g.session_token = session_token
            
            # Check if user has required role
            if user.role.name != role_name:
                return {'error': 'Insufficient role', 'code': 'INSUFFICIENT_ROLE'}, 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def optional_auth(f):
    """
    Decorator for optional authentication.
    If user is authenticated, g.current_user will be set.
    If not authenticated, g.current_user will be None.
    
    Usage:
        @optional_auth
        def public_route():
            if g.current_user:
                # User is authenticated
                pass
            else:
                # User is not authenticated
                pass
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_token = _extract_session_token()
        
        # Initialize g.current_user as None
        g.current_user = None
        g.session_token = None
        
        if session_token:
            # Get auth service
            auth_service = current_app.extensions.get('auth_service')
            if auth_service:
                # Get user by session
                user = auth_service.get_user_by_session(session_token)
                if user and user.is_active():
                    g.current_user = user
                    g.session_token = session_token
                    request.user_id = user.id
        
        return f(*args, **kwargs)
    
    return decorated_function


def get_current_user():
    """
    Get current authenticated user from g.
    
    Returns:
        User object or None
    """
    return getattr(g, 'current_user', None)


def get_current_session_token():
    """
    Get current session token from g.
    
    Returns:
        Session token string or None
    """
    return getattr(g, 'session_token', None)


def is_authenticated():
    """
    Check if current user is authenticated.
    
    Returns:
        True if authenticated, False otherwise
    """
    return get_current_user() is not None


def has_permission(permission: str):
    """
    Check if current user has specific permission.
    
    Args:
        permission: Permission name to check
        
    Returns:
        True if user has permission, False otherwise
    """
    user = get_current_user()
    if not user:
        return False
    
    return user.role.has_permission(permission)


def has_role(role_name: str):
    """
    Check if current user has specific role.
    
    Args:
        role_name: Role name to check
        
    Returns:
        True if user has role, False otherwise
    """
    user = get_current_user()
    if not user:
        return False
    
    return user.role.name == role_name


def is_admin():
    """
    Check if current user is admin.
    
    Returns:
        True if user is admin, False otherwise
    """
    return has_role('Admin')


def is_customer():
    """
    Check if current user is a customer (registered or guest).
    
    Returns:
        True if user is customer, False otherwise
    """
    return has_role('RegisteredCustomer') or has_role('GuestCustomer')


def get_user_id():
    """
    Get current user ID.
    
    Returns:
        User ID or None
    """
    user = get_current_user()
    if user:
        return user.id

    return getattr(request, 'user_id', None)


def get_user_email():
    """
    Get current user email.
    
    Returns:
        User email or None
    """
    user = get_current_user()
    return user.email if user else None


def get_user_role():
    """
    Get current user role name.
    
    Returns:
        Role name or None
    """
    user = get_current_user()
    return user.role.name if user else None
