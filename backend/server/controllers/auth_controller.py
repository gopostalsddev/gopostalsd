"""
Authentication Controller for Go Postal SD Application

This module contains the business logic for authentication operations.
It follows the same pattern as other controllers for clean separation of concerns.
"""

from server.controllers import Result
import logging
import traceback

logger = logging.getLogger(__name__)


class AuthController:
    """
    Controller for handling authentication operations.
    Implements the Controller pattern for clean separation of concerns.
    """

    @staticmethod
    def register_user(email: str, password: str, first_name: str, last_name: str,
                     shipping_address: dict, billing_address: dict = None) -> Result:
        """
        Register a new user.
        
        Args:
            email: User's email address
            password: User's password
            first_name: User's first name
            last_name: User's last name
            shipping_address: Shipping address information
            billing_address: Billing address information (optional)
            
        Returns:
            Result containing registration result
        """
        result = Result()
        
        # Debug: Log method entry with input parameters
        logger.debug(f"AuthController.register_user called with:")
        logger.debug(f"  email: {email}")
        logger.debug(f"  first_name: {first_name}")
        logger.debug(f"  last_name: {last_name}")
        logger.debug(f"  shipping_address: {shipping_address}")
        logger.debug(f"  billing_address: {billing_address}")
        logger.debug(f"  password length: {len(password) if password else 'None'}")
        
        try:
            # Get auth service from app context
            from flask import current_app
            logger.debug("Getting auth service from app context...")
            auth_service = current_app.extensions.get('auth_service')
            
            if not auth_service:
                logger.error("Authentication service not available in app extensions")
                result.status = False
                result.error = "Authentication service not available"
                return result
            
            logger.debug("Auth service found, proceeding with registration...")
            
            # Register user
            logger.debug("Calling auth_service.register_user...")
            registration_result = auth_service.register_user(
                email, password, first_name, last_name, shipping_address, billing_address
            )
            
            logger.debug(f"Registration result received: {registration_result}")
            
            if registration_result['success']:
                logger.info(f"User registration successful for email: {email}")
                result.data = registration_result
            else:
                logger.warning(f"User registration failed for email: {email}, error: {registration_result['error']}")
                result.status = False
                result.error = registration_result['error']
                result.details = registration_result.get('code')
            
        except Exception as e:
            logger.error(f"Exception in register_user for email {email}: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Exception traceback: {traceback.format_exc()}")
            result.status = False
            result.error = f"Registration failed: {str(e)}"
            
        logger.debug(f"AuthController.register_user returning result: {result}")
        return result

    @staticmethod
    def verify_email(token: str) -> Result:
        """
        Verify user email with token.
        
        Args:
            token: Email verification token
            
        Returns:
            Result containing verification result
        """
        result = Result()
        
        try:
            # Get auth service from app context
            from flask import current_app
            auth_service = current_app.extensions.get('auth_service')
            
            if not auth_service:
                result.status = False
                result.error = "Authentication service not available"
                return result
            
            # Verify email
            verification_result = auth_service.verify_email(token)
            
            if verification_result['success']:
                result.data = verification_result
            else:
                result.status = False
                result.error = verification_result['error']
                result.details = verification_result.get('code')
            
        except Exception as e:
            logger.error(f"Error verifying email: {str(e)}")
            result.status = False
            result.error = f"Email verification failed: {str(e)}"
            
        return result

    @staticmethod
    def login(email: str, password: str, ip_address: str = None, user_agent: str = None) -> Result:
        """
        Authenticate user login.
        
        Args:
            email: User's email
            password: User's password
            ip_address: Client IP address
            user_agent: Client user agent
            
        Returns:
            Result containing login result
        """
        result = Result()
        
        try:
            # Get auth service from app context
            from flask import current_app
            auth_service = current_app.extensions.get('auth_service')
            
            if not auth_service:
                result.status = False
                result.error = "Authentication service not available"
                return result
            
            # Login user
            login_result = auth_service.login(email, password, ip_address, user_agent)
            
            if login_result['success']:
                result.data = login_result
            else:
                result.status = False
                result.error = login_result['error']
                result.details = login_result.get('code')
                # Pass through additional error data (email verification or other)
                result.data = login_result
            
        except Exception as e:
            logger.error(f"Error during login: {str(e)}")
            result.status = False
            result.error = f"Login failed: {str(e)}"
            
        return result

    @staticmethod
    def logout(session_token: str) -> Result:
        """
        Logout user by invalidating session.
        
        Args:
            session_token: Session token to invalidate
            
        Returns:
            Result containing logout result
        """
        result = Result()
        
        try:
            # Get auth service from app context
            from flask import current_app
            auth_service = current_app.extensions.get('auth_service')
            
            if not auth_service:
                result.status = False
                result.error = "Authentication service not available"
                return result
            
            # Logout user
            logout_result = auth_service.logout(session_token)
            
            if logout_result['success']:
                result.data = logout_result
            else:
                result.status = False
                result.error = logout_result['error']
                result.details = logout_result.get('code')
            
        except Exception as e:
            logger.error(f"Error during logout: {str(e)}")
            result.status = False
            result.error = f"Logout failed: {str(e)}"
            
        return result

    @staticmethod
    def refresh_session(refresh_token: str) -> Result:
        """
        Refresh user session with refresh token.
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            Result containing refresh result
        """
        result = Result()
        
        try:
            # Get auth service from app context
            from flask import current_app
            auth_service = current_app.extensions.get('auth_service')
            
            if not auth_service:
                result.status = False
                result.error = "Authentication service not available"
                return result
            
            # Refresh session
            refresh_result = auth_service.refresh_session(refresh_token)
            
            if refresh_result['success']:
                result.data = refresh_result
            else:
                result.status = False
                result.error = refresh_result['error']
                result.details = refresh_result.get('code')
            
        except Exception as e:
            logger.error(f"Error refreshing session: {str(e)}")
            result.status = False
            result.error = f"Session refresh failed: {str(e)}"
            
        return result

    @staticmethod
    def resend_verification_email(email: str) -> Result:
        """
        Resend verification email for user.
        
        Args:
            email: User's email address
            
        Returns:
            Result containing request result
        """
        result = Result()
        
        try:
            # Get auth service from app context
            from flask import current_app
            auth_service = current_app.extensions.get('auth_service')
            
            if not auth_service:
                result.status = False
                result.error = "Authentication service not available"
                return result
            
            # Resend verification email
            resend_result = auth_service.resend_verification_email(email)
            
            if resend_result['success']:
                result.data = resend_result
            else:
                result.status = False
                result.error = resend_result['error']
                result.details = resend_result.get('code')
            
        except Exception as e:
            logger.error(f"Error resending verification email: {str(e)}")
            result.status = False
            result.error = f"Failed to resend verification email: {str(e)}"
            
        return result

    @staticmethod
    def request_password_reset(email: str) -> Result:
        """
        Request password reset for user.
        
        Args:
            email: User's email address
            
        Returns:
            Result containing request result
        """
        result = Result()
        
        try:
            # Get auth service from app context
            from flask import current_app
            auth_service = current_app.extensions.get('auth_service')
            
            if not auth_service:
                result.status = False
                result.error = "Authentication service not available"
                return result
            
            # Request password reset
            reset_result = auth_service.request_password_reset(email)
            
            if reset_result['success']:
                result.data = reset_result
            else:
                result.status = False
                result.error = reset_result['error']
                result.details = reset_result.get('code')
            
        except Exception as e:
            logger.error(f"Error requesting password reset: {str(e)}")
            result.status = False
            result.error = f"Password reset request failed: {str(e)}"
            
        return result

    @staticmethod
    def reset_password(token: str, new_password: str) -> Result:
        """
        Reset user password with token.
        
        Args:
            token: Password reset token
            new_password: New password
            
        Returns:
            Result containing reset result
        """
        result = Result()
        
        try:
            # Get auth service from app context
            from flask import current_app
            auth_service = current_app.extensions.get('auth_service')
            
            if not auth_service:
                result.status = False
                result.error = "Authentication service not available"
                return result
            
            # Reset password
            reset_result = auth_service.reset_password(token, new_password)
            
            if reset_result['success']:
                result.data = reset_result
            else:
                result.status = False
                result.error = reset_result['error']
                result.details = reset_result.get('code')
            
        except Exception as e:
            logger.error(f"Error resetting password: {str(e)}")
            result.status = False
            result.error = f"Password reset failed: {str(e)}"
            
        return result

    @staticmethod
    def get_current_user(session_token: str) -> Result:
        """
        Get current user by session token.
        
        Args:
            session_token: Session token
            
        Returns:
            Result containing user information
        """
        result = Result()
        
        try:
            # Get auth service from app context
            from flask import current_app
            auth_service = current_app.extensions.get('auth_service')
            
            if not auth_service:
                result.status = False
                result.error = "Authentication service not available"
                return result
            
            # Get user by session
            user = auth_service.get_user_by_session(session_token)
            
            if user:
                result.data = {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role.name,
                    'email_verified': user.email_verified,
                    'status': user.status.value,
                    'created_at': user.created_at.isoformat() if user.created_at else None,
                    'last_login': user.last_login.isoformat() if user.last_login else None
                }
            else:
                result.status = False
                result.error = "Invalid or expired session"
                result.details = "INVALID_SESSION"
            
        except Exception as e:
            logger.error(f"Error getting current user: {str(e)}")
            result.status = False
            result.error = f"Failed to get user: {str(e)}"
            
        return result

    @staticmethod
    def validate_password_strength(password: str) -> Result:
        """
        Validate password strength.
        
        Args:
            password: Password to validate
            
        Returns:
            Result containing validation result
        """
        result = Result()
        
        try:
            # Get password service from app context
            from flask import current_app
            password_service = current_app.extensions.get('password_service')
            
            if not password_service:
                result.status = False
                result.error = "Password service not available"
                return result
            
            # Validate password
            validation_result = password_service.validate_password_strength(password)
            result.data = validation_result
            
        except Exception as e:
            logger.error(f"Error validating password: {str(e)}")
            result.status = False
            result.error = f"Password validation failed: {str(e)}"
            
        return result
