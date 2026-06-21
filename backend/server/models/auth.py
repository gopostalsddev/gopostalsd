"""
Authentication Models for Go Postal SD Application

This module contains all authentication-related models including users, roles, sessions,
password reset tokens, email verification tokens, and OAuth providers.
"""

from server.config import database as db
from datetime import datetime, timedelta
import secrets
import hashlib
from enum import Enum


class UserStatus(Enum):
    """User account status enumeration."""
    PENDING_VERIFICATION = "pending_verification"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEACTIVATED = "deactivated"


class AuthProvider(Enum):
    """Authentication provider enumeration."""
    LOCAL = "local"
    GOOGLE = "google"
    FACEBOOK = "facebook"
    APPLE = "apple"


class User(db.Model):
    """
    Enhanced User model with authentication capabilities.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(60), nullable=False)
    last_name = db.Column(db.String(60), nullable=False)
    # Legacy compatibility columns for older local SQLite schemas.
    legacy_email_address = db.Column('email_address', db.String(120), nullable=True)
    legacy_creation_date = db.Column('creation_date', db.DateTime, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=True)  # Nullable for OAuth users
    status = db.Column(db.Enum(UserStatus), default=UserStatus.PENDING_VERIFICATION, nullable=False)
    email_verified = db.Column(db.Boolean, default=False, nullable=False)
    email_verified_at = db.Column(db.DateTime, nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    failed_login_attempts = db.Column(db.Integer, default=0, nullable=False)
    locked_until = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Foreign key for addresses
    shipping_address_id = db.Column(db.Integer, db.ForeignKey('addresses.id'), nullable=True)
    billing_address_id = db.Column(db.Integer, db.ForeignKey('addresses.id'), nullable=True)

    # Foreign key to Role
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)

    # Relationships
    shipping_address = db.relationship('Address', foreign_keys=[shipping_address_id], backref='shipping_users')
    billing_address = db.relationship('Address', foreign_keys=[billing_address_id], backref='billing_users')
    role = db.relationship('Role', backref='users')
    sessions = db.relationship('UserSession', backref='user', cascade='all, delete-orphan')
    password_reset_tokens = db.relationship('PasswordResetToken', backref='user', cascade='all, delete-orphan')
    email_verification_tokens = db.relationship('EmailVerificationToken', backref='user', cascade='all, delete-orphan')
    oauth_accounts = db.relationship('OAuthAccount', backref='user', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<User {self.email}>"

    def is_locked(self):
        """Check if user account is locked due to failed login attempts."""
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        return False

    def is_active(self):
        """Check if user account is active."""
        return self.status == UserStatus.ACTIVE and not self.is_locked()

    def can_login(self):
        """Check if user can login (active and not locked)."""
        return self.is_active() and self.email_verified

    def get_full_name(self):
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"


class Role(db.Model):
    """
    Role model for role-based access control.
    """
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    permissions = db.Column(db.JSON, nullable=True)  # Store permissions as JSON
    is_system_role = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Role {self.name}>"

    def has_permission(self, permission):
        """Check if role has specific permission."""
        if not self.permissions:
            return False
        return permission in self.permissions


class Permission(db.Model):
    """
    Permission model for granular access control.
    """
    __tablename__ = 'permissions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    resource = db.Column(db.String(50), nullable=False)  # e.g., 'users', 'products', 'orders'
    action = db.Column(db.String(50), nullable=False)    # e.g., 'create', 'read', 'update', 'delete'
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Permission {self.name}>"


class UserSession(db.Model):
    """
    User session model for session management.
    """
    __tablename__ = 'user_sessions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_token = db.Column(db.String(255), unique=True, nullable=False, index=True)
    refresh_token = db.Column(db.String(255), unique=True, nullable=True, index=True)
    ip_address = db.Column(db.String(45), nullable=True)  # IPv6 compatible
    user_agent = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<UserSession {self.session_token[:10]}...>"

    def is_expired(self):
        """Check if session is expired."""
        return datetime.utcnow() > self.expires_at

    @staticmethod
    def generate_tokens():
        """Generate session and refresh tokens."""
        session_token = secrets.token_urlsafe(32)
        refresh_token = secrets.token_urlsafe(32)
        return session_token, refresh_token


class PasswordResetToken(db.Model):
    """
    Password reset token model for password recovery.
    """
    __tablename__ = 'password_reset_tokens'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    used_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<PasswordResetToken {self.token[:10]}...>"

    def is_expired(self):
        """Check if token is expired."""
        return datetime.utcnow() > self.expires_at

    def is_valid(self):
        """Check if token is valid (not expired and not used)."""
        return not self.is_expired() and not self.used

    @staticmethod
    def generate_token():
        """Generate a secure password reset token."""
        return secrets.token_urlsafe(32)


class EmailVerificationToken(db.Model):
    """
    Email verification token model for email confirmation.
    """
    __tablename__ = 'email_verification_tokens'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    used_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<EmailVerificationToken {self.token[:10]}...>"

    def is_expired(self):
        """Check if token is expired."""
        return datetime.utcnow() > self.expires_at

    def is_valid(self):
        """Check if token is valid (not expired and not used)."""
        return not self.is_expired() and not self.used

    @staticmethod
    def generate_token():
        """Generate a secure email verification token."""
        return secrets.token_urlsafe(32)


class OAuthAccount(db.Model):
    """
    OAuth account model for third-party authentication.
    """
    __tablename__ = 'oauth_accounts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    provider = db.Column(db.Enum(AuthProvider), nullable=False)
    provider_user_id = db.Column(db.String(255), nullable=False)
    provider_email = db.Column(db.String(120), nullable=True)
    access_token = db.Column(db.Text, nullable=True)
    refresh_token = db.Column(db.Text, nullable=True)
    token_expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Unique constraint on provider and provider_user_id
    __table_args__ = (db.UniqueConstraint('provider', 'provider_user_id', name='_provider_user_uc'),)

    def __repr__(self):
        return f"<OAuthAccount {self.provider.value}:{self.provider_user_id}>"

    def is_token_expired(self):
        """Check if OAuth token is expired."""
        if not self.token_expires_at:
            return False
        return datetime.utcnow() > self.token_expires_at


class Address(db.Model):
    """
    Address model for user addresses.
    """
    __tablename__ = 'addresses'

    id = db.Column(db.Integer, primary_key=True)
    street = db.Column(db.String(180), nullable=False)
    city = db.Column(db.String(180), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    zip_code = db.Column(db.String(20), nullable=False)  # Changed to String for international support
    country = db.Column(db.String(180), nullable=False)
    apt = db.Column(db.String(50), nullable=True)
    is_default = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Address {self.street}, {self.city}, {self.country}>"


class Account(db.Model):
    """
    Legacy account model (keeping for backward compatibility).
    """
    __tablename__ = 'accounts'
    username = db.Column(db.String(100), primary_key=True)


class HashingAlgorithm(db.Model):
    """
    Legacy hashing algorithm model (keeping for backward compatibility).
    """
    __tablename__ = 'hashing_algorithms'
    id = db.Column(db.Integer, primary_key=True)
