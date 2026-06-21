"""
Authentication Routes for Go Postal SD Application

This module defines all authentication-related API endpoints using Flask-RESTX.
It follows the same pattern as other route modules for consistency.
"""

from flask import request
from flask_restx import Namespace, Resource, fields
from server.controllers.auth_controller import AuthController

# Create namespace for authentication operations
api = Namespace('auth', description='Authentication operations')

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
    def post(self):
        """Register a new user."""
        data = request.get_json()
        
        if not data:
            return {'error': 'Request body is required'}, 400
        
        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name', 'shipping_address']
        for field in required_fields:
            if field not in data:
                return {'error': f'{field} is required'}, 400
        
        # Validate address fields
        address_fields = ['street', 'city', 'state', 'zip_code', 'country']
        for field in address_fields:
            if field not in data['shipping_address']:
                return {'error': f'shipping_address.{field} is required'}, 400
        
        result = AuthController.register_user(
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            shipping_address=data['shipping_address'],
            billing_address=data.get('billing_address')
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
            return {'error': 'Token is required'}, 400
        
        result = AuthController.verify_email(token)
        
        if result.status:
            return result.data, 200
        else:
            return {'error': result.error, 'code': result.details}, 400

@api.route('/resend-verification')
class ResendVerificationResource(Resource):
    """Resource for resending email verification."""
    
    @api.doc('resend_verification')
    @api.expect(api.model('ResendVerification', {
        'email': fields.String(required=True, description='User email address')
    }))
    def post(self):
        """Resend email verification link."""
        data = request.get_json()
        
        if not data or 'email' not in data:
            return {'error': 'Email is required'}, 400
        
        result = AuthController.resend_verification_email(data['email'])
        
        if result.status:
            return result.data, 200
        else:
            return {'error': result.error, 'code': result.details}, 400


@api.route('/login')
class LoginResource(Resource):
    """Resource for user login."""
    
    @api.doc('login_user')
    @api.expect(login_model)
    def post(self):
        """Authenticate user login."""
        data = request.get_json()
        
        if not data:
            return {'error': 'Request body is required'}, 400
        
        if 'email' not in data or 'password' not in data:
            return {'error': 'Email and password are required'}, 400
        
        # Get client information
        ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
        user_agent = request.environ.get('HTTP_USER_AGENT')
        
        result = AuthController.login(
            email=data['email'],
            password=data['password'],
            ip_address=ip_address,
            user_agent=user_agent
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
        session_token = request.args.get('session_token')
        
        if not session_token:
            return {'error': 'Session token is required'}, 400
        
        result = AuthController.logout(session_token)
        
        if result.status:
            return result.data, 200
        else:
            return {'error': result.error, 'code': result.details}, 400

@api.route('/refresh')
class RefreshResource(Resource):
    """Resource for session refresh."""
    
    @api.doc('refresh_session')
    @api.param('refresh_token', 'Refresh token', required=True)
    @api.marshal_with(session_model)
    def post(self):
        """Refresh user session with refresh token."""
        refresh_token = request.args.get('refresh_token')
        
        if not refresh_token:
            return {'error': 'Refresh token is required'}, 400
        
        result = AuthController.refresh_session(refresh_token)
        
        if result.status:
            return result.data, 200
        else:
            return {'error': result.error, 'code': result.details}, 401

@api.route('/password-reset/request')
class PasswordResetRequestResource(Resource):
    """Resource for password reset requests."""
    
    @api.doc('request_password_reset')
    @api.expect(password_reset_request_model)
    def post(self):
        """Request password reset for user."""
        data = request.get_json()
        
        if not data or 'email' not in data:
            return {'error': 'Email is required'}, 400
        
        result = AuthController.request_password_reset(data['email'])
        
        if result.status:
            return result.data, 200
        else:
            return {'error': result.error, 'code': result.details}, 400

@api.route('/password-reset')
class PasswordResetResource(Resource):
    """Resource for password reset."""
    
    @api.doc('reset_password')
    @api.expect(password_reset_model)
    def post(self):
        """Reset user password with token."""
        data = request.get_json()
        
        if not data:
            return {'error': 'Request body is required'}, 400
        
        if 'token' not in data or 'new_password' not in data:
            return {'error': 'Token and new_password are required'}, 400
        
        result = AuthController.reset_password(data['token'], data['new_password'])
        
        if result.status:
            return result.data, 200
        else:
            return {'error': result.error, 'code': result.details}, 400

@api.route('/me')
class CurrentUserResource(Resource):
    """Resource for current user information."""
    
    @api.doc('get_current_user')
    @api.param('session_token', 'Session token', required=True)
    @api.marshal_with(user_model)
    def get(self):
        """Get current user by session token."""
        session_token = request.args.get('session_token')
        
        if not session_token:
            return {'error': 'Session token is required'}, 400
        
        result = AuthController.get_current_user(session_token)
        
        if result.status:
            return result.data, 200
        else:
            return {'error': result.error, 'code': result.details}, 401

@api.route('/validate-password')
class PasswordValidationResource(Resource):
    """Resource for password validation."""
    
    @api.doc('validate_password')
    @api.expect(password_validation_model)
    @api.marshal_with(password_validation_response_model)
    def post(self):
        """Validate password strength."""
        data = request.get_json()
        
        if not data or 'password' not in data:
            return {'error': 'Password is required'}, 400
        
        result = AuthController.validate_password_strength(data['password'])
        
        if result.status:
            return result.data, 200
        else:
            return {'error': result.error}, 400
