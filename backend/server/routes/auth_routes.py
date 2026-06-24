"""
Authentication Routes for Go Postal SD Application

This module defines all authentication-related API endpoints using Flask-RESTX.
It follows the same pattern as other route modules for consistency.
"""

from flask import request, current_app
from flask_restx import Namespace, Resource, fields
import re
from server.controllers.auth_controller import AuthController
from server.validation.input_validator import (
    validate_address_input,
    validate_email_input,
    validate_password_input,
    validate_string_input,
)
from server.middleware.rate_limit_middleware import rate_limit_by_ip
from server.routes.response_utils import error_response

# Create namespace for authentication operations
api = Namespace('auth', description='Authentication operations')


def _extract_bearer_token() -> str:
    """Extract bearer token from Authorization header."""
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        return auth_header.split(' ', 1)[1].strip()
    return ''


def _validate_auth_token(raw_token: str, max_length: int = 255):
    """Validate auth tokens without applying generic SQL/XSS string rules."""
    if raw_token is None:
        return ''

    token = str(raw_token).strip()
    if not token or len(token) > max_length:
        return ''

    # Support common token formats (URL-safe/base64/JWT-like).
    if not re.fullmatch(r'[A-Za-z0-9._~+/=-]+', token):
        return ''

    return token


def _get_auth_service():
    return current_app.extensions.get('auth_service')


def _get_password_service():
    return current_app.extensions.get('password_service')

# Define models for API documentation
address_model = api.model('Address', {
    'street': fields.String(description='Street address'),
    'city': fields.String(description='City'),
    'state': fields.String(description='State/Province'),
    'zip_code': fields.String(description='ZIP/Postal code'),
    'country': fields.String(description='Country'),
    'apt': fields.String(description='Apartment/Suite number')
})

user_model = api.model('User', {
    'id': fields.Integer(description='User ID'),
    'email': fields.String(description='Email address'),
    'first_name': fields.String(description='First name'),
    'last_name': fields.String(description='Last name'),
    'role': fields.String(description='User role'),
    'email_verified': fields.Boolean(description='Email verified status'),
    'status': fields.String(description='User status'),
    'created_at': fields.DateTime(description='Created timestamp'),
    'last_login': fields.DateTime(description='Last login timestamp'),
    'address': fields.Nested(address_model, description='Shipping address', allow_null=True),
    'shipping_address': fields.Nested(address_model, description='Shipping address', allow_null=True),
    'billing_address': fields.Nested(address_model, description='Billing address', allow_null=True)
})

registration_model = api.model('RegistrationRequest', {
    'email': fields.String(description='Email address', required=True),
    'password': fields.String(description='Password', required=True),
    'first_name': fields.String(description='First name', required=True),
    'last_name': fields.String(description='Last name', required=True),
    'shipping_address': fields.Nested(address_model, description='Shipping address', required=True),
    'billing_address': fields.Nested(address_model, description='Billing address')
})

login_model = api.model('LoginRequest', {
    'email': fields.String(description='Email address', required=True),
    'password': fields.String(description='Password', required=True)
})

password_reset_request_model = api.model('PasswordResetRequest', {
    'email': fields.String(description='Email address', required=True)
})

password_reset_model = api.model('PasswordReset', {
    'token': fields.String(description='Reset token', required=True),
    'new_password': fields.String(description='New password', required=True)
})

password_validation_model = api.model('PasswordValidation', {
    'password': fields.String(description='Password to validate', required=True)
})

session_model = api.model('Session', {
    'session_token': fields.String(description='Session token'),
    'refresh_token': fields.String(description='Refresh token'),
    'expires_at': fields.DateTime(description='Expiration timestamp')
})

login_response_model = api.model('LoginResponse', {
    'user': fields.Nested(user_model, description='User information'),
    'session': fields.Nested(session_model, description='Session information')
})

registration_response_model = api.model('RegistrationResponse', {
    'user_id': fields.Integer(description='User ID'),
    'email': fields.String(description='Email address'),
    'message': fields.String(description='Response message'),
    'verification_required': fields.Boolean(description='Email verification required')
})

password_validation_response_model = api.model('PasswordValidationResponse', {
    'is_valid': fields.Boolean(description='Password validity'),
    'errors': fields.List(fields.String, description='Validation errors'),
    'warnings': fields.List(fields.String, description='Validation warnings'),
    'strength_score': fields.Integer(description='Strength score (0-100)'),
    'strength_level': fields.String(description='Strength level')
})

# Define resources
@api.route('/register')
class RegistrationResource(Resource):
    """Resource for user registration."""
    
    @api.doc('register_user')
    @api.expect(registration_model)
    @rate_limit_by_ip('AUTH_REGISTER_RATE_LIMIT_COUNT', 'AUTH_REGISTER_RATE_LIMIT_WINDOW_SECONDS', 'auth-register')
    def post(self):
        """Register a new user."""
        data = request.get_json(silent=True)
        
        if not data:
            return error_response('Request body is required', 400)
        
        email_result = validate_email_input(data.get('email'))
        password_result = validate_password_input(data.get('password'))
        first_name_result = validate_string_input(data.get('first_name'), max_length=100)
        last_name_result = validate_string_input(data.get('last_name'), max_length=100)

        shipping_address_result = validate_address_input(data.get('shipping_address') or {})
        if not shipping_address_result.is_valid:
            return error_response('Invalid shipping_address', 400)

        billing_address = data.get('billing_address')
        billing_address_result = None
        if billing_address:
            billing_address_result = validate_address_input(billing_address)
            if not billing_address_result.is_valid:
                return error_response('Invalid billing_address', 400)

        if not email_result.is_valid:
            return error_response('Invalid email', 400)
        if not password_result.is_valid:
            return error_response('Invalid password', 400)
        if not first_name_result.is_valid or not last_name_result.is_valid:
            return error_response('Invalid first_name or last_name', 400)
        
        result = AuthController.register_user(
            email=email_result.sanitized_data,
            password=data['password'],
            first_name=first_name_result.sanitized_data,
            last_name=last_name_result.sanitized_data,
            shipping_address=shipping_address_result.sanitized_data,
            billing_address=billing_address_result.sanitized_data if billing_address_result else None,
            auth_service=_get_auth_service(),
        )
        
        if result.status:
            return result.data, 201
        else:
            # Return appropriate HTTP status code based on error type
            status_code = 400
            if result.details == 'USER_EXISTS':
                status_code = 409  # Conflict
            elif result.details == 'ROLE_NOT_FOUND':
                status_code = 500  # Internal Server Error
            elif result.details == 'VALIDATION_ERROR':
                status_code = 422  # Unprocessable Entity
            
            return {
                'error': result.error, 
                'code': result.details,
                'message': result.error  # Add message field for consistency
            }, status_code

@api.route('/verify-email')
class EmailVerificationResource(Resource):
    """Resource for email verification."""
    
    @api.doc('verify_email')
    @api.param('token', 'Email verification token', required=True)
    def get(self):
        """Verify user email with token."""
        token = request.args.get('token')
        
        if not token:
            return error_response('Token is required', 400)
        
        token_result = validate_string_input(token, max_length=255)
        if not token_result.is_valid:
            return error_response('Invalid token', 400)

        result = AuthController.verify_email(token_result.sanitized_data, auth_service=_get_auth_service())
        
        if result.status:
            return result.data, 200
        else:
            return error_response(result.error, 400, code=result.details, category='authentication')

    @api.doc('verify_email_post')
    @api.expect(api.model('EmailVerificationRequest', {
        'token': fields.String(required=True, description='Email verification token')
    }))
    def post(self):
        """Verify user email with token in request body."""
        data = request.get_json(silent=True) or {}
        token = data.get('token')

        if not token:
            return error_response('Token is required', 400)

        token_result = validate_string_input(token, max_length=255)
        if not token_result.is_valid:
            return error_response('Invalid token', 400)

        result = AuthController.verify_email(token_result.sanitized_data, auth_service=_get_auth_service())

        if result.status:
            return result.data, 200
        return error_response(result.error, 400, code=result.details, category='authentication')

@api.route('/resend-verification')
class ResendVerificationResource(Resource):
    """Resource for resending email verification."""
    
    @api.doc('resend_verification')
    @api.expect(api.model('ResendVerification', {
        'email': fields.String(required=True, description='User email address')
    }))
    def post(self):
        """Resend email verification link."""
        data = request.get_json(silent=True)
        
        if not data or 'email' not in data:
            return error_response('Email is required', 400)

        email_result = validate_email_input(data.get('email'))
        if not email_result.is_valid:
            return error_response('Invalid email', 400)
        
        result = AuthController.resend_verification_email(email_result.sanitized_data, auth_service=_get_auth_service())
        
        if result.status:
            return result.data, 200
        else:
            return error_response(result.error, 400, code=result.details, category='authentication')


@api.route('/login')
class LoginResource(Resource):
    """Resource for user login."""
    
    @api.doc('login_user')
    @api.expect(login_model)
    @rate_limit_by_ip('AUTH_LOGIN_RATE_LIMIT_COUNT', 'AUTH_LOGIN_RATE_LIMIT_WINDOW_SECONDS', 'auth-login')
    def post(self):
        """Authenticate user login."""
        data = request.get_json(silent=True)
        
        if not data:
            return error_response('Request body is required', 400)
        
        if 'email' not in data or 'password' not in data:
            return error_response('Email and password are required', 400)

        email_result = validate_email_input(data.get('email'))
        if not email_result.is_valid:
            return error_response('Invalid email or password format', 400)
        
        # Get client information
        ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
        user_agent = request.environ.get('HTTP_USER_AGENT')
        
        result = AuthController.login(
            email=email_result.sanitized_data,
            password=data['password'],
            ip_address=ip_address,
            user_agent=user_agent,
            auth_service=_get_auth_service(),
        )
        
        if result.status:
            # Successful login - marshal the response
            from flask_restx import marshal
            return marshal(result.data, login_response_model), 200
        else:
            # Error response
            response = {'error': result.error, 'code': result.details}
            # Include additional data for email verification
            if result.data:
                response.update(result.data)
            
            return response, 401

@api.route('/logout')
class LogoutResource(Resource):
    """Resource for user logout."""
    
    @api.doc('logout_user')
    @api.param('session_token', 'Session token', required=True)
    def post(self):
        """Logout user by invalidating session."""
        data = request.get_json(silent=True) or {}
        session_token = data.get('session_token') or _extract_bearer_token() or request.args.get('session_token')
        
        if not session_token:
            return error_response('Session token is required', 400)

        validated_token = _validate_auth_token(session_token)
        if not validated_token:
            return error_response('Invalid session token', 400)

        result = AuthController.logout(validated_token, auth_service=_get_auth_service())
        
        if result.status:
            return result.data, 200
        else:
            return error_response(result.error, 400, code=result.details, category='authentication')

@api.route('/refresh')
class RefreshResource(Resource):
    """Resource for session refresh."""
    
    @api.doc('refresh_session')
    @api.param('refresh_token', 'Refresh token', required=True)
    @api.response(200, 'Session refreshed successfully', session_model)
    def post(self):
        """Refresh user session with refresh token."""
        data = request.get_json(silent=True) or {}
        refresh_token = data.get('refresh_token') or request.args.get('refresh_token')
        
        if not refresh_token:
            return error_response('Refresh token is required', 400)

        validated_token = _validate_auth_token(refresh_token)
        if not validated_token:
            return error_response('Invalid refresh token', 400)

        result = AuthController.refresh_session(validated_token, auth_service=_get_auth_service())
        
        if result.status:
            return result.data, 200
        else:
            return error_response(result.error, 401, code=result.details, category='authentication')

@api.route('/password-reset/request')
class PasswordResetRequestResource(Resource):
    """Resource for password reset requests."""
    
    @api.doc('request_password_reset')
    @api.expect(password_reset_request_model)
    @rate_limit_by_ip('AUTH_PASSWORD_RESET_RATE_LIMIT_COUNT', 'AUTH_PASSWORD_RESET_RATE_LIMIT_WINDOW_SECONDS', 'auth-password-reset-request')
    def post(self):
        """Request password reset for user."""
        data = request.get_json(silent=True)
        
        if not data or 'email' not in data:
            return error_response('Email is required', 400)
        
        email_result = validate_email_input(data.get('email'))
        if not email_result.is_valid:
            return error_response('Invalid email', 400)

        result = AuthController.request_password_reset(email_result.sanitized_data, auth_service=_get_auth_service())
        
        if result.status:
            return result.data, 200
        else:
            return error_response(result.error, 400, code=result.details, category='authentication')

@api.route('/password-reset')
class PasswordResetResource(Resource):
    """Resource for password reset."""
    
    @api.doc('reset_password')
    @api.expect(password_reset_model)
    def post(self):
        """Reset user password with token."""
        data = request.get_json(silent=True)
        
        if not data:
            return error_response('Request body is required', 400)
        
        if 'token' not in data or 'new_password' not in data:
            return error_response('Token and new_password are required', 400)

        token_result = validate_string_input(data.get('token'), max_length=255)
        password_result = validate_password_input(data.get('new_password'))
        if not token_result.is_valid:
            return error_response('Invalid token', 400)
        if not password_result.is_valid:
            return error_response('Invalid new_password', 400)
        
        result = AuthController.reset_password(token_result.sanitized_data, data['new_password'], auth_service=_get_auth_service())
        
        if result.status:
            return result.data, 200
        else:
            return error_response(result.error, 400, code=result.details, category='authentication')

@api.route('/me')
class CurrentUserResource(Resource):
    """Resource for current user information."""
    
    @api.doc('get_current_user')
    @api.param('session_token', 'Session token', required=True)
    @api.response(200, 'Current user fetched successfully', user_model)
    def get(self):
        """Get current user by session token."""
        session_token = _extract_bearer_token() or request.args.get('session_token')
        
        if not session_token:
            return error_response('Session token is required', 400)

        validated_token = _validate_auth_token(session_token)
        if not validated_token:
            return error_response('Invalid session token', 400)

        result = AuthController.get_current_user(validated_token, auth_service=_get_auth_service())
        
        if result.status:
            return result.data, 200
        else:
            return error_response(result.error, 401, code=result.details, category='authentication')

@api.route('/validate-password')
class PasswordValidationResource(Resource):
    """Resource for password validation."""
    
    @api.doc('validate_password')
    @api.expect(password_validation_model)
    @api.response(200, 'Password validated', password_validation_response_model)
    def post(self):
        """Validate password strength."""
        data = request.get_json(silent=True)
        
        if not data or 'password' not in data:
            return error_response('Password is required', 400)
        
        password_result = validate_string_input(data.get('password'), max_length=128)
        if not password_result.is_valid:
            return error_response('Invalid password', 400)

        result = AuthController.validate_password_strength(data['password'], password_service=_get_password_service())
        
        if result.status:
            return result.data, 200
        else:
            return error_response(result.error, 400, code='PASSWORD_VALIDATION_ERROR', category='validation')
