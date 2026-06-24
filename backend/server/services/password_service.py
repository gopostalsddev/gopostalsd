"""
Password Service for Go Postal SD Application

This module handles password hashing, verification, and strength validation.
"""

import hashlib
import secrets
import re
import hmac
import logging
from typing import Dict, Any
from flask import current_app

logger = logging.getLogger(__name__)


class PasswordService:
    """
    Service for password operations including hashing, verification, and validation.
    """

    def __init__(self):
        # Password strength requirements
        self.min_length = 8
        self.max_length = 128
        self.require_uppercase = True
        self.require_lowercase = True
        self.require_digits = True
        self.require_special_chars = True
        self.special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        self.hash_iterations = self._get_hash_iterations()

    @staticmethod
    def _get_hash_iterations() -> int:
        try:
            configured = current_app.config.get('PASSWORD_HASH_ITERATIONS', 100000)
            return int(configured)
        except Exception:
            return 100000

    def hash_password(self, password: str) -> str:
        """
        Hash a password using PBKDF2 with salt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
        """
        try:
            # Generate a random salt
            salt = secrets.token_hex(32)
            
            # Hash the password with salt using PBKDF2
            password_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                self.hash_iterations
            )
            
            # Combine salt and hash
            return f"{salt}:{password_hash.hex()}"
            
        except Exception as e:
            logger.error(f"Error hashing password: {str(e)}")
            raise

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password: Plain text password
            hashed_password: Hashed password string
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            # Split salt and hash
            salt, password_hash = hashed_password.split(':')
            
            # Hash the provided password with the same salt
            test_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                self.hash_iterations
            )
            
            # Compare hashes
            return hmac.compare_digest(test_hash.hex(), password_hash)
            
        except Exception as e:
            logger.error(f"Error verifying password: {str(e)}")
            return False

    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """
        Validate password strength against requirements.
        
        Args:
            password: Password to validate
            
        Returns:
            Dict containing validation result and details
        """
        errors = []
        warnings = []
        
        # Check length
        if len(password) < self.min_length:
            errors.append(f"Password must be at least {self.min_length} characters long")
        elif len(password) > self.max_length:
            errors.append(f"Password must be no more than {self.max_length} characters long")
        
        # Check for uppercase letters
        if self.require_uppercase and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        # Check for lowercase letters
        if self.require_lowercase and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        # Check for digits
        if self.require_digits and not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")
        
        # Check for special characters
        if self.require_special_chars and not re.search(f'[{re.escape(self.special_chars)}]', password):
            errors.append(f"Password must contain at least one special character ({self.special_chars})")
        
        # Check for common patterns
        if self._is_common_password(password):
            warnings.append("This password is commonly used and may be easily guessed")
        
        if self._has_repeating_patterns(password):
            warnings.append("Password contains repeating patterns which may be weak")
        
        # Calculate strength score
        strength_score = self._calculate_strength_score(password)
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'strength_score': strength_score,
            'strength_level': self._get_strength_level(strength_score)
        }

    def generate_secure_password(self, length: int = 16) -> str:
        """
        Generate a secure random password.
        
        Args:
            length: Password length (default 16)
            
        Returns:
            Generated password string
        """
        try:
            # Ensure minimum length
            length = max(length, self.min_length)
            
            # Character sets
            lowercase = 'abcdefghijklmnopqrstuvwxyz'
            uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            digits = '0123456789'
            special = self.special_chars
            
            # Ensure at least one character from each required set
            password = [
                secrets.choice(lowercase),
                secrets.choice(uppercase),
                secrets.choice(digits),
                secrets.choice(special)
            ]
            
            # Fill remaining length with random characters from all sets
            all_chars = lowercase + uppercase + digits + special
            for _ in range(length - 4):
                password.append(secrets.choice(all_chars))
            
            # Shuffle the password
            secrets.SystemRandom().shuffle(password)
            
            return ''.join(password)
            
        except Exception as e:
            logger.error(f"Error generating password: {str(e)}")
            raise

    def _is_common_password(self, password: str) -> bool:
        """Check if password is in common passwords list."""
        common_passwords = {
            'password', '123456', '123456789', 'qwerty', 'abc123',
            'password123', 'admin', 'letmein', 'welcome', 'monkey',
            '1234567890', 'password1', 'qwerty123', 'dragon', 'master'
        }
        return password.lower() in common_passwords

    def _has_repeating_patterns(self, password: str) -> bool:
        """Check for repeating patterns in password."""
        # Check for repeated characters
        if re.search(r'(.)\1{2,}', password):
            return True
        
        # Check for sequential patterns
        if re.search(r'(012|123|234|345|456|567|678|789|890)', password):
            return True
        
        if re.search(r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)', password.lower()):
            return True
        
        return False

    def _calculate_strength_score(self, password: str) -> int:
        """Calculate password strength score (0-100)."""
        score = 0
        
        # Length score (0-30 points)
        if len(password) >= 8:
            score += 10
        if len(password) >= 12:
            score += 10
        if len(password) >= 16:
            score += 10
        
        # Character variety score (0-40 points)
        if re.search(r'[a-z]', password):
            score += 10
        if re.search(r'[A-Z]', password):
            score += 10
        if re.search(r'\d', password):
            score += 10
        if re.search(f'[{re.escape(self.special_chars)}]', password):
            score += 10
        
        # Complexity score (0-30 points)
        if len(set(password)) >= len(password) * 0.7:  # 70% unique characters
            score += 15
        if not self._is_common_password(password):
            score += 15
        
        return min(score, 100)

    def _get_strength_level(self, score: int) -> str:
        """Get strength level based on score."""
        if score < 30:
            return 'Very Weak'
        elif score < 50:
            return 'Weak'
        elif score < 70:
            return 'Fair'
        elif score < 90:
            return 'Good'
        else:
            return 'Strong'
