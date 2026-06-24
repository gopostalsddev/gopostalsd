"""
Comprehensive Input Validation System for Go Postal SD Application

This module provides robust input validation, sanitization, and security features
for production-ready data handling.
"""

import re
import html
import bleach
import uuid
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from email_validator import validate_email, EmailNotValidError
try:
    from marshmallow import Schema, fields, ValidationError as MarshmallowValidationError
    from marshmallow.validate import Length, Range, OneOf, Regexp, Email
    MARSHMALLOW_AVAILABLE = True
except ImportError:
    Schema = object
    fields = None
    MarshmallowValidationError = Exception
    Length = Range = OneOf = Regexp = Email = None
    MARSHMALLOW_AVAILABLE = False
import logging

logger = logging.getLogger(__name__)


class ValidationResult:
    """Result of validation operation."""
    
    def __init__(self, is_valid: bool = True, errors: List[str] = None, sanitized_data: Any = None):
        self.is_valid = is_valid
        self.errors = errors or []
        self.sanitized_data = sanitized_data
    
    def add_error(self, error: str):
        """Add validation error."""
        self.errors.append(error)
        self.is_valid = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'is_valid': self.is_valid,
            'errors': self.errors,
            'sanitized_data': self.sanitized_data
        }


class InputValidator:
    """Comprehensive input validation and sanitization."""
    
    def __init__(self):
        self.max_string_length = 1000
        self.max_text_length = 10000
        self.allowed_html_tags = ['b', 'i', 'em', 'strong', 'p', 'br', 'ul', 'ol', 'li']
        self.allowed_html_attributes = {}
        
        # Security patterns
        self.sql_injection_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT)\b)",
            r"(--|#|\/\*|\*\/)",
            r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
            r"(\b(OR|AND)\s+'.*?'\s*=\s*'.*?')",
        ]
        
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>.*?</iframe>",
            r"<object[^>]*>.*?</object>",
            r"<embed[^>]*>.*?</embed>",
        ]
    
    def validate_email(self, email: str) -> ValidationResult:
        """Validate email address."""
        result = ValidationResult()
        
        if not email or not isinstance(email, str):
            result.add_error("Email is required")
            return result
        
        email = email.strip().lower()
        
        try:
            validated_email = validate_email(email)
            result.sanitized_data = validated_email.email
        except EmailNotValidError as e:
            result.add_error(f"Invalid email format: {str(e)}")
        
        return result
    
    def validate_password(self, password: str) -> ValidationResult:
        """Validate password strength."""
        result = ValidationResult()
        
        if not password or not isinstance(password, str):
            result.add_error("Password is required")
            return result
        
        password = password.strip()
        
        # Length validation
        if len(password) < 8:
            result.add_error("Password must be at least 8 characters long")
        
        if len(password) > 128:
            result.add_error("Password must be no more than 128 characters long")
        
        # Character requirements
        if not re.search(r'[A-Z]', password):
            result.add_error("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', password):
            result.add_error("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', password):
            result.add_error("Password must contain at least one digit")
        
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
            result.add_error("Password must contain at least one special character")
        
        # Check for common patterns
        if self._is_common_password(password):
            result.add_error("Password is too common and easily guessable")
        
        if result.is_valid:
            result.sanitized_data = password
        
        return result
    
    def validate_string(self, value: Any, max_length: int = None, allow_html: bool = False) -> ValidationResult:
        """Validate and sanitize string input."""
        result = ValidationResult()
        
        if value is None:
            result.sanitized_data = ""
            return result
        
        if not isinstance(value, str):
            value = str(value)
        
        # Length validation
        max_len = max_length or self.max_string_length
        if len(value) > max_len:
            result.add_error(f"String exceeds maximum length of {max_len} characters")
            return result
        
        # Security validation
        if self._contains_sql_injection(value):
            result.add_error("Input contains potentially malicious SQL content")
            return result
        
        if self._contains_xss(value):
            result.add_error("Input contains potentially malicious script content")
            return result
        
        # Sanitization
        sanitized = value.strip()
        
        if not allow_html:
            # Remove HTML tags
            sanitized = bleach.clean(sanitized, tags=[], attributes={})
        else:
            # Allow only safe HTML tags
            sanitized = bleach.clean(
                sanitized,
                tags=self.allowed_html_tags,
                attributes=self.allowed_html_attributes
            )
        
        # HTML encode special characters
        sanitized = html.escape(sanitized, quote=True)
        
        result.sanitized_data = sanitized
        return result
    
    def validate_number(self, value: Any, min_value: float = None, max_value: float = None, 
                       integer_only: bool = False) -> ValidationResult:
        """Validate numeric input."""
        result = ValidationResult()
        
        if value is None:
            result.add_error("Number is required")
            return result
        
        try:
            if integer_only:
                num_value = int(value)
            else:
                num_value = float(value)
        except (ValueError, TypeError):
            result.add_error("Invalid number format")
            return result
        
        # Range validation
        if min_value is not None and num_value < min_value:
            result.add_error(f"Number must be at least {min_value}")
        
        if max_value is not None and num_value > max_value:
            result.add_error(f"Number must be no more than {max_value}")
        
        if result.is_valid:
            result.sanitized_data = num_value
        
        return result
    
    def validate_decimal(self, value: Any, precision: int = 2) -> ValidationResult:
        """Validate decimal/money input."""
        result = ValidationResult()
        
        if value is None:
            result.add_error("Decimal value is required")
            return result
        
        try:
            decimal_value = Decimal(str(value))
            # Round to specified precision
            decimal_value = decimal_value.quantize(Decimal('0.01'))
        except (InvalidOperation, ValueError, TypeError):
            result.add_error("Invalid decimal format")
            return result
        
        if decimal_value < 0:
            result.add_error("Decimal value cannot be negative")
        
        if result.is_valid:
            result.sanitized_data = decimal_value
        
        return result
    
    def validate_uuid(self, value: Any) -> ValidationResult:
        """Validate UUID format."""
        result = ValidationResult()
        
        if not value:
            result.add_error("UUID is required")
            return result
        
        try:
            uuid_value = uuid.UUID(str(value))
            result.sanitized_data = str(uuid_value)
        except (ValueError, TypeError):
            result.add_error("Invalid UUID format")
        
        return result
    
    def validate_date(self, value: Any, format_string: str = "%Y-%m-%d") -> ValidationResult:
        """Validate date input."""
        result = ValidationResult()
        
        if not value:
            result.add_error("Date is required")
            return result
        
        if isinstance(value, date):
            result.sanitized_data = value
            return result
        
        if isinstance(value, datetime):
            result.sanitized_data = value.date()
            return result
        
        try:
            if isinstance(value, str):
                date_value = datetime.strptime(value.strip(), format_string).date()
            else:
                date_value = datetime.fromisoformat(str(value)).date()
            
            result.sanitized_data = date_value
        except (ValueError, TypeError):
            result.add_error(f"Invalid date format. Expected: {format_string}")
        
        return result
    
    def validate_phone(self, value: Any) -> ValidationResult:
        """Validate phone number."""
        result = ValidationResult()
        
        if not value:
            result.add_error("Phone number is required")
            return result
        
        # Remove all non-digit characters
        phone_digits = re.sub(r'\D', '', str(value))
        
        # Validate US phone number format
        if len(phone_digits) == 10:
            result.sanitized_data = f"({phone_digits[:3]}) {phone_digits[3:6]}-{phone_digits[6:]}"
        elif len(phone_digits) == 11 and phone_digits[0] == '1':
            result.sanitized_data = f"({phone_digits[1:4]}) {phone_digits[4:7]}-{phone_digits[7:]}"
        else:
            result.add_error("Invalid phone number format")
        
        return result
    
    def validate_address(self, address_data: Dict[str, Any]) -> ValidationResult:
        """Validate address data."""
        result = ValidationResult()
        
        required_fields = ['street', 'city', 'state', 'zip_code', 'country']
        
        for field in required_fields:
            if field not in address_data or not address_data[field]:
                result.add_error(f"Address {field} is required")
        
        if not result.is_valid:
            return result
        
        # Validate individual fields
        street_result = self.validate_string(address_data['street'], max_length=200)
        if not street_result.is_valid:
            result.errors.extend(street_result.errors)
        
        city_result = self.validate_string(address_data['city'], max_length=100)
        if not city_result.is_valid:
            result.errors.extend(city_result.errors)
        
        state_result = self.validate_string(address_data['state'], max_length=50)
        if not state_result.is_valid:
            result.errors.extend(state_result.errors)
        
        zip_result = self.validate_string(address_data['zip_code'], max_length=20)
        if not zip_result.is_valid:
            result.errors.extend(zip_result.errors)
        
        country_result = self.validate_string(address_data['country'], max_length=100)
        if not country_result.is_valid:
            result.errors.extend(country_result.errors)
        
        if result.is_valid:
            result.sanitized_data = {
                'street': street_result.sanitized_data,
                'city': city_result.sanitized_data,
                'state': state_result.sanitized_data,
                'zip_code': zip_result.sanitized_data,
                'country': country_result.sanitized_data,
                'apt': self.validate_string(address_data.get('apt', ''), max_length=50).sanitized_data
            }
        
        return result
    
    def validate_file_upload(self, file_data: Dict[str, Any], 
                           allowed_types: List[str] = None,
                           max_size: int = 10 * 1024 * 1024) -> ValidationResult:  # 10MB default
        """Validate file upload."""
        result = ValidationResult()
        
        if not file_data:
            result.add_error("File data is required")
            return result
        
        # Check file size
        if file_data.get('size', 0) > max_size:
            result.add_error(f"File size exceeds maximum limit of {max_size // (1024*1024)}MB")
        
        # Check file type
        allowed_types = allowed_types or ['image/jpeg', 'image/png', 'image/gif', 'application/pdf']
        if file_data.get('type') not in allowed_types:
            result.add_error(f"File type not allowed. Allowed types: {', '.join(allowed_types)}")
        
        # Check filename
        filename = file_data.get('filename', '')
        if not filename or len(filename) > 255:
            result.add_error("Invalid filename")
        
        # Check for malicious filenames
        if self._is_malicious_filename(filename):
            result.add_error("Filename contains potentially malicious content")
        
        if result.is_valid:
            result.sanitized_data = {
                'filename': self.validate_string(filename).sanitized_data,
                'type': file_data['type'],
                'size': file_data['size'],
                'content': file_data.get('content')
            }
        
        return result
    
    def _contains_sql_injection(self, value: str) -> bool:
        """Check for SQL injection patterns."""
        for pattern in self.sql_injection_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        return False
    
    def _contains_xss(self, value: str) -> bool:
        """Check for XSS patterns."""
        for pattern in self.xss_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        return False
    
    def _is_common_password(self, password: str) -> bool:
        """Check if password is commonly used."""
        common_passwords = [
            'password', '123456', '123456789', 'qwerty', 'abc123',
            'password123', 'admin', 'letmein', 'welcome', 'monkey'
        ]
        return password.lower() in common_passwords
    
    def _is_malicious_filename(self, filename: str) -> bool:
        """Check for malicious filename patterns."""
        malicious_patterns = [
            r'\.\./',  # Path traversal
            r'<script',  # Script tags
            r'javascript:',  # JavaScript protocol
            r'data:',  # Data protocol
        ]
        
        for pattern in malicious_patterns:
            if re.search(pattern, filename, re.IGNORECASE):
                return True
        return False


# Global validator instance
validator = InputValidator()


# Convenience functions
def validate_email_input(email: str) -> ValidationResult:
    """Validate email input."""
    return validator.validate_email(email)


def validate_password_input(password: str) -> ValidationResult:
    """Validate password input."""
    return validator.validate_password(password)


def validate_string_input(value: Any, max_length: int = None, allow_html: bool = False) -> ValidationResult:
    """Validate string input."""
    return validator.validate_string(value, max_length, allow_html)


def validate_number_input(value: Any, min_value: float = None, max_value: float = None, 
                         integer_only: bool = False) -> ValidationResult:
    """Validate number input."""
    return validator.validate_number(value, min_value, max_value, integer_only)


def validate_decimal_input(value: Any, precision: int = 2) -> ValidationResult:
    """Validate decimal input."""
    return validator.validate_decimal(value, precision)


def validate_address_input(address_data: Dict[str, Any]) -> ValidationResult:
    """Validate address input."""
    return validator.validate_address(address_data)


def validate_file_input(file_data: Dict[str, Any], allowed_types: List[str] = None, 
                       max_size: int = 10 * 1024 * 1024) -> ValidationResult:
    """Validate file input."""
    return validator.validate_file_upload(file_data, allowed_types, max_size)


if MARSHMALLOW_AVAILABLE:
    # Marshmallow schemas for API validation
    class UserRegistrationSchema(Schema):
        """Schema for user registration validation."""
        email = fields.Email(required=True, validate=Length(max=255))
        password = fields.Str(required=True, validate=Length(min=8, max=128))
        first_name = fields.Str(required=True, validate=Length(min=1, max=100))
        last_name = fields.Str(required=True, validate=Length(min=1, max=100))
        shipping_address = fields.Dict(required=True)
        billing_address = fields.Dict(required=False)


    class AddressSchema(Schema):
        """Schema for address validation."""
        street = fields.Str(required=True, validate=Length(min=1, max=200))
        city = fields.Str(required=True, validate=Length(min=1, max=100))
        state = fields.Str(required=True, validate=Length(min=1, max=50))
        zip_code = fields.Str(required=True, validate=Length(min=1, max=20))
        country = fields.Str(required=True, validate=Length(min=1, max=100))
        apt = fields.Str(required=False, validate=Length(max=50))


    class ProductSchema(Schema):
        """Schema for product validation."""
        name = fields.Str(required=True, validate=Length(min=1, max=200))
        description = fields.Str(required=False, validate=Length(max=2000))
        price = fields.Decimal(required=True, places=2)
        category = fields.Str(required=True, validate=Length(min=1, max=100))
        sku = fields.Str(required=True, validate=Length(min=1, max=100))


    class CartItemSchema(Schema):
        """Schema for cart item validation."""
        product_id = fields.Int(required=True, validate=Range(min=1))
        quantity = fields.Int(required=True, validate=Range(min=1, max=100))
        selected_options = fields.List(fields.Int(), required=False)


    # Global schema instances
    user_registration_schema = UserRegistrationSchema()
    address_schema = AddressSchema()
    product_schema = ProductSchema()
    cart_item_schema = CartItemSchema()
else:
    user_registration_schema = None
    address_schema = None
    product_schema = None
    cart_item_schema = None
