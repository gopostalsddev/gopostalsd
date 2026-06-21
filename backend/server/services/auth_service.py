"""
Authentication Service for Go Postal SD Application

This module contains the business logic for user authentication, registration,
password management, and session handling.
"""

import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from server.config import database as db
from server.models.auth import (
    User, Role, UserSession, PasswordResetToken, EmailVerificationToken,
    OAuthAccount, Address, UserStatus, AuthProvider
)
from server.services.email_service import EmailService
from server.services.password_service import PasswordService

logger = logging.getLogger(__name__)


class AuthService:
    """
    Service for handling authentication operations.
    Implements the Service pattern for clean separation of concerns.
    """

    def __init__(self, email_service: EmailService, password_service: PasswordService):
        self.email_service = email_service
        self.password_service = password_service

    def register_user(self, email: str, password: str, first_name: str, last_name: str,
                     shipping_address: Dict[str, Any], billing_address: Dict[str, Any] = None) -> Dict[str, Any]:
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
            Dict containing registration result
        """
        logger.debug(f"AuthService.register_user called with email: {email}")
        
        try:
            # Input validation
            if not email or not isinstance(email, str) or not email.strip():
                return {
                    'success': False,
                    'error': 'Email is required',
                    'code': 'VALIDATION_ERROR'
                }
            
            if not password or not isinstance(password, str) or len(password) < 8:
                return {
                    'success': False,
                    'error': 'Password must be at least 8 characters long',
                    'code': 'VALIDATION_ERROR'
                }
            
            if not first_name or not isinstance(first_name, str) or not first_name.strip():
                return {
                    'success': False,
                    'error': 'First name is required',
                    'code': 'VALIDATION_ERROR'
                }
            
            if not last_name or not isinstance(last_name, str) or not last_name.strip():
                return {
                    'success': False,
                    'error': 'Last name is required',
                    'code': 'VALIDATION_ERROR'
                }
            
            # Validate email format
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email.strip()):
                return {
                    'success': False,
                    'error': 'Please enter a valid email address',
                    'code': 'INVALID_EMAIL'
                }
            
            # Check if user already exists
            logger.debug(f"Checking if user exists with email: {email.strip().lower()}")
            existing_user = User.query.filter_by(email=email.strip().lower()).first()
            if existing_user:
                logger.info(f"User registration failed - user already exists: {email}")
                return {
                    'success': False,
                    'error': 'An account with this email already exists. Please try logging in instead.',
                    'code': 'USER_EXISTS'
                }

            # Get default role (RegisteredCustomer)
            default_role = Role.query.filter_by(name='RegisteredCustomer').first()
            if not default_role:
                return {
                    'success': False,
                    'error': 'Default role not found',
                    'code': 'ROLE_NOT_FOUND'
                }

            # Create shipping address
            shipping_addr = Address(
                street=shipping_address['street'],
                city=shipping_address['city'],
                state=shipping_address['state'],
                zip_code=shipping_address['zip_code'],
                country=shipping_address['country'],
                apt=shipping_address.get('apt'),
                is_default=True
            )
            db.session.add(shipping_addr)
            db.session.flush()  # Get the ID

            # Create billing address (use shipping if not provided)
            if billing_address:
                billing_addr = Address(
                    street=billing_address['street'],
                    city=billing_address['city'],
                    state=billing_address['state'],
                    zip_code=billing_address['zip_code'],
                    country=billing_address['country'],
                    apt=billing_address.get('apt'),
                    is_default=False
                )
                db.session.add(billing_addr)
                db.session.flush()
            else:
                billing_addr = shipping_addr

            # Hash password
            password_hash = self.password_service.hash_password(password)

            # Create user
            user = User(
                email=email,
                legacy_email_address=email,
                legacy_creation_date=datetime.utcnow(),
                password_hash=password_hash,
                first_name=first_name,
                last_name=last_name,
                role_id=default_role.id,
                shipping_address_id=shipping_addr.id,
                billing_address_id=billing_addr.id,
                status=UserStatus.PENDING_VERIFICATION
            )
            db.session.add(user)
            db.session.flush()  # Get the user ID

            # Generate email verification token
            verification_token = self._create_email_verification_token(user.id)

            # Send verification email
            self.email_service.send_verification_email(
                user.email, user.first_name, verification_token.token
            )

            db.session.commit()

            return {
                'success': True,
                'user_id': user.id,
                'email': user.email,
                'message': 'Registration successful. Please check your email for verification.',
                'verification_required': True
            }

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error registering user: {str(e)}")
            return {
                'success': False,
                'error': 'Registration failed',
                'code': 'REGISTRATION_ERROR'
            }

    def verify_email(self, token: str) -> Dict[str, Any]:
        """
        Verify user email with token.
        
        Args:
            token: Email verification token
            
        Returns:
            Dict containing verification result
        """
        try:
            logger.info(f"Verifying email with token: {token[:20]}...")
            verification_token = EmailVerificationToken.query.filter_by(
                token=token, used=False
            ).first()

            if not verification_token:
                logger.warning(f"Verification token not found or already used")
                return {
                    'success': False,
                    'error': 'Invalid or expired verification token',
                    'code': 'INVALID_TOKEN'
                }

            if verification_token.is_expired():
                return {
                    'success': False,
                    'error': 'Verification token has expired',
                    'code': 'TOKEN_EXPIRED'
                }

            # Update user status
            user = verification_token.user
            user.email_verified = True
            user.email_verified_at = datetime.utcnow()
            user.status = UserStatus.ACTIVE

            # Mark token as used
            verification_token.used = True
            verification_token.used_at = datetime.utcnow()

            db.session.commit()

            return {
                'success': True,
                'message': 'Email verified successfully',
                'user_id': user.id
            }

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error verifying email: {str(e)}")
            return {
                'success': False,
                'error': 'Email verification failed',
                'code': 'VERIFICATION_ERROR'
            }

    def resend_verification_email(self, email: str) -> Dict[str, Any]:
        """
        Resend email verification email.
        
        Args:
            email: User's email
            
        Returns:
            Dict containing result
        """
        try:
            user = User.query.filter_by(email=email).first()
            
            if not user:
                # Don't reveal if user exists for security
                return {
                    'success': True,
                    'message': 'If an account exists with this email, a verification link has been sent'
                }
            
            if user.email_verified:
                return {
                    'success': True,
                    'message': 'Email already verified'
                }
            
            # Create new verification token
            verification_token = self._create_email_verification_token(user.id)
            
            db.session.commit()
            
            # Send verification email
            self.email_service.send_verification_email(
                email=user.email,
                first_name=user.first_name,
                token=verification_token.token
            )
            
            logger.info(f"Verification email resent for user: {user.email}")
            
            return {
                'success': True,
                'message': 'Verification email has been sent'
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error resending verification email: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to resend verification email',
                'code': 'RESEND_ERROR'
            }

    def login(self, email: str, password: str, ip_address: str = None, user_agent: str = None) -> Dict[str, Any]:
        """
        Authenticate user login.
        
        Args:
            email: User's email
            password: User's password
            ip_address: Client IP address
            user_agent: Client user agent
            
        Returns:
            Dict containing login result
        """
        try:
            user = User.query.filter_by(email=email).first()

            if not user:
                return {
                    'success': False,
                    'error': 'Invalid email or password',
                    'code': 'INVALID_CREDENTIALS'
                }

            # Check if account is locked
            if user.is_locked():
                return {
                    'success': False,
                    'error': 'Account is temporarily locked due to too many failed attempts',
                    'code': 'ACCOUNT_LOCKED'
                }

            # Check if account is suspended or deactivated (but not pending verification)
            if user.status.value == 'suspended':
                return {
                    'success': False,
                    'error': 'Your account has been suspended',
                    'code': 'ACCOUNT_SUSPENDED'
                }
            elif user.status.value == 'deactivated':
                return {
                    'success': False,
                    'error': 'Your account has been deactivated',
                    'code': 'ACCOUNT_DEACTIVATED'
                }

            # Check if email is verified (applies to pending_verification status)
            if not user.email_verified:
                # Invalidate any existing sessions for this user
                UserSession.query.filter_by(user_id=user.id, is_active=True).update({'is_active': False})
                db.session.commit()
                
                return {
                    'success': False,
                    'error': 'Please verify your email before logging in',
                    'code': 'EMAIL_NOT_VERIFIED',
                    'email': user.email,
                    'user_id': user.id,
                    'requires_verification': True
                }
            
            # If we get here and status is not ACTIVE, there's a problem
            if user.status != UserStatus.ACTIVE:
                return {
                    'success': False,
                    'error': 'Account is not active',
                    'code': 'ACCOUNT_INACTIVE'
                }

            # Verify password
            password_matches = self.password_service.verify_password(password, user.password_hash)
            
            if not password_matches:
                logger.warning(f"Password verification failed for user: {user.email}")
                # Increment failed login attempts
                user.failed_login_attempts += 1
                
                # Lock account after 5 failed attempts for 30 minutes
                if user.failed_login_attempts >= 5:
                    user.locked_until = datetime.utcnow() + timedelta(minutes=30)
                
                db.session.commit()
                
                return {
                    'success': False,
                    'error': 'Invalid email or password',
                    'code': 'INVALID_CREDENTIALS'
                }

            # Reset failed login attempts and update last login
            user.failed_login_attempts = 0
            user.locked_until = None
            user.last_login = datetime.utcnow()

            # Create session
            session_token, refresh_token = UserSession.generate_tokens()
            session = UserSession(
                user_id=user.id,
                session_token=session_token,
                refresh_token=refresh_token,
                ip_address=ip_address,
                user_agent=user_agent,
                expires_at=datetime.utcnow() + timedelta(days=7)  # 7 days session
            )
            db.session.add(session)
            db.session.commit()

            return {
                'success': True,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role.name,
                    'email_verified': user.email_verified
                },
                'session': {
                    'session_token': session_token,
                    'refresh_token': refresh_token,
                    'expires_at': session.expires_at.isoformat()
                }
            }

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error during login: {str(e)}")
            return {
                'success': False,
                'error': 'Login failed',
                'code': 'LOGIN_ERROR'
            }

    def logout(self, session_token: str) -> Dict[str, Any]:
        """
        Logout user by invalidating session.
        
        Args:
            session_token: Session token to invalidate
            
        Returns:
            Dict containing logout result
        """
        try:
            session = UserSession.query.filter_by(
                session_token=session_token, is_active=True
            ).first()

            if session:
                session.is_active = False
                db.session.commit()

            return {
                'success': True,
                'message': 'Logged out successfully'
            }

        except Exception as e:
            logger.error(f"Error during logout: {str(e)}")
            return {
                'success': False,
                'error': 'Logout failed',
                'code': 'LOGOUT_ERROR'
            }

    def refresh_session(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh user session with refresh token.
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            Dict containing refresh result
        """
        try:
            session = UserSession.query.filter_by(
                refresh_token=refresh_token, is_active=True
            ).first()

            if not session or session.is_expired():
                return {
                    'success': False,
                    'error': 'Invalid or expired refresh token',
                    'code': 'INVALID_REFRESH_TOKEN'
                }

            # Generate new tokens
            new_session_token, new_refresh_token = UserSession.generate_tokens()
            
            # Update session
            session.session_token = new_session_token
            session.refresh_token = new_refresh_token
            session.expires_at = datetime.utcnow() + timedelta(days=7)
            session.last_accessed = datetime.utcnow()

            db.session.commit()

            return {
                'success': True,
                'session': {
                    'session_token': new_session_token,
                    'refresh_token': new_refresh_token,
                    'expires_at': session.expires_at.isoformat()
                }
            }

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error refreshing session: {str(e)}")
            return {
                'success': False,
                'error': 'Session refresh failed',
                'code': 'REFRESH_ERROR'
            }

    def request_password_reset(self, email: str) -> Dict[str, Any]:
        """
        Request password reset for user.
        
        Args:
            email: User's email address
            
        Returns:
            Dict containing request result
        """
        try:
            user = User.query.filter_by(email=email).first()

            if not user:
                # Don't reveal if user exists or not
                return {
                    'success': True,
                    'message': 'If an account with this email exists, a password reset link has been sent.'
                }

            # Create password reset token
            reset_token = self._create_password_reset_token(user.id)
            db.session.commit()

            # Send password reset email
            self.email_service.send_password_reset_email(
                user.email, user.first_name, reset_token.token
            )

            return {
                'success': True,
                'message': 'If an account with this email exists, a password reset link has been sent.'
            }

        except Exception as e:
            logger.error(f"Error requesting password reset: {str(e)}")
            return {
                'success': False,
                'error': 'Password reset request failed',
                'code': 'RESET_REQUEST_ERROR'
            }

    def reset_password(self, token: str, new_password: str) -> Dict[str, Any]:
        """
        Reset user password with token.
        
        Args:
            token: Password reset token
            new_password: New password
            
        Returns:
            Dict containing reset result
        """
        try:
            reset_token = PasswordResetToken.query.filter_by(
                token=token, used=False
            ).first()

            if not reset_token or reset_token.is_expired():
                return {
                    'success': False,
                    'error': 'Invalid or expired reset token',
                    'code': 'INVALID_TOKEN'
                }

            # Update user password
            user = reset_token.user
            new_password_hash = self.password_service.hash_password(new_password)
            user.password_hash = new_password_hash
            user.failed_login_attempts = 0
            user.locked_until = None

            # Mark token as used
            reset_token.used = True
            reset_token.used_at = datetime.utcnow()

            # Invalidate all user sessions
            UserSession.query.filter_by(user_id=user.id, is_active=True).update({'is_active': False})

            db.session.commit()
            logger.info(f"Password successfully reset for user: {user.email}")

            return {
                'success': True,
                'message': 'Password reset successfully'
            }

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error resetting password: {str(e)}")
            return {
                'success': False,
                'error': 'Password reset failed',
                'code': 'RESET_ERROR'
            }

    def get_user_by_session(self, session_token: str) -> Optional[User]:
        """
        Get user by session token.
        
        Args:
            session_token: Session token
            
        Returns:
            User object or None
        """
        try:
            session = UserSession.query.filter_by(
                session_token=session_token, is_active=True
            ).first()

            if not session or session.is_expired():
                return None

            user = session.user
            
            # Verify user's email is verified and account is active
            if not user.email_verified:
                # Invalidate this session and all other sessions for this user
                UserSession.query.filter_by(user_id=user.id, is_active=True).update({'is_active': False})
                db.session.commit()
                return None
            
            if user.status != UserStatus.ACTIVE:
                # Invalidate this session and all other sessions for this user
                UserSession.query.filter_by(user_id=user.id, is_active=True).update({'is_active': False})
                db.session.commit()
                return None

            # Update last accessed
            session.last_accessed = datetime.utcnow()
            db.session.commit()

            return user

        except Exception as e:
            logger.error(f"Error getting user by session: {str(e)}")
            return None

    def _create_email_verification_token(self, user_id: int) -> EmailVerificationToken:
        """Create email verification token for user."""
        token = EmailVerificationToken.generate_token()
        verification_token = EmailVerificationToken(
            user_id=user_id,
            token=token,
            expires_at=datetime.utcnow() + timedelta(hours=24)  # 24 hours expiry
        )
        db.session.add(verification_token)
        return verification_token

    def _create_password_reset_token(self, user_id: int) -> PasswordResetToken:
        """Create password reset token for user."""
        token = PasswordResetToken.generate_token()
        reset_token = PasswordResetToken(
            user_id=user_id,
            token=token,
            expires_at=datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry
        )
        db.session.add(reset_token)
        return reset_token
