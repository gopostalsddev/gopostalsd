"""
Authentication Controller for Go Postal SD Application.

Controller methods are thin adapters around services and support optional
dependency injection to improve testability.
"""

from flask import current_app

from server.controllers import Result
from server.models.auth import Address


class AuthController:
    """Controller for handling authentication operations."""

    @staticmethod
    def _get_service(name: str, provided_service=None):
        if provided_service is not None:
            return provided_service
        return current_app.extensions.get(name)

    @staticmethod
    def _service_unavailable_result(message: str) -> Result:
        result = Result(status=False)
        result.error = message
        return result

    @staticmethod
    def _map_service_result(payload: dict) -> Result:
        result = Result()
        if payload.get('success'):
            result.data = payload
            return result

        result.status = False
        result.error = payload.get('error', 'Operation failed')
        result.details = payload.get('code')
        result.data = payload
        return result

    @staticmethod
    def register_user(
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        shipping_address: dict,
        billing_address: dict = None,
        auth_service=None,
    ) -> Result:
        service = AuthController._get_service('auth_service', auth_service)
        if not service:
            return AuthController._service_unavailable_result('Authentication service not available')

        return AuthController._map_service_result(
            service.register_user(email, password, first_name, last_name, shipping_address, billing_address)
        )

    @staticmethod
    def verify_email(token: str, auth_service=None) -> Result:
        service = AuthController._get_service('auth_service', auth_service)
        if not service:
            return AuthController._service_unavailable_result('Authentication service not available')

        return AuthController._map_service_result(service.verify_email(token))

    @staticmethod
    def login(email: str, password: str, ip_address: str = None, user_agent: str = None, auth_service=None) -> Result:
        service = AuthController._get_service('auth_service', auth_service)
        if not service:
            return AuthController._service_unavailable_result('Authentication service not available')

        return AuthController._map_service_result(service.login(email, password, ip_address, user_agent))

    @staticmethod
    def logout(session_token: str, auth_service=None) -> Result:
        service = AuthController._get_service('auth_service', auth_service)
        if not service:
            return AuthController._service_unavailable_result('Authentication service not available')

        return AuthController._map_service_result(service.logout(session_token))

    @staticmethod
    def refresh_session(refresh_token: str, auth_service=None) -> Result:
        service = AuthController._get_service('auth_service', auth_service)
        if not service:
            return AuthController._service_unavailable_result('Authentication service not available')

        return AuthController._map_service_result(service.refresh_session(refresh_token))

    @staticmethod
    def resend_verification_email(email: str, auth_service=None) -> Result:
        service = AuthController._get_service('auth_service', auth_service)
        if not service:
            return AuthController._service_unavailable_result('Authentication service not available')

        return AuthController._map_service_result(service.resend_verification_email(email))

    @staticmethod
    def request_password_reset(email: str, auth_service=None) -> Result:
        service = AuthController._get_service('auth_service', auth_service)
        if not service:
            return AuthController._service_unavailable_result('Authentication service not available')

        return AuthController._map_service_result(service.request_password_reset(email))

    @staticmethod
    def reset_password(token: str, new_password: str, auth_service=None) -> Result:
        service = AuthController._get_service('auth_service', auth_service)
        if not service:
            return AuthController._service_unavailable_result('Authentication service not available')

        return AuthController._map_service_result(service.reset_password(token, new_password))

    @staticmethod
    def get_current_user(session_token: str, auth_service=None) -> Result:
        result = Result()
        service = AuthController._get_service('auth_service', auth_service)
        if not service:
            return AuthController._service_unavailable_result('Authentication service not available')

        user = service.get_user_by_session(session_token)
        if not user:
            result.status = False
            result.error = 'Invalid or expired session'
            result.details = 'INVALID_SESSION'
            return result

        shipping_address = None
        billing_address = None

        if user.shipping_address_id:
            shipping_addr = Address.query.get(user.shipping_address_id)
            if shipping_addr:
                shipping_address = {
                    'street': shipping_addr.street,
                    'city': shipping_addr.city,
                    'state': shipping_addr.state,
                    'zip_code': shipping_addr.zip_code,
                    'country': shipping_addr.country,
                    'apt': shipping_addr.apt or '',
                }

        if user.billing_address_id:
            billing_addr = Address.query.get(user.billing_address_id)
            if billing_addr:
                billing_address = {
                    'street': billing_addr.street,
                    'city': billing_addr.city,
                    'state': billing_addr.state,
                    'zip_code': billing_addr.zip_code,
                    'country': billing_addr.country,
                    'apt': billing_addr.apt or '',
                }

        result.data = {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role.name,
            'email_verified': user.email_verified,
            'status': user.status.value,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'address': shipping_address,
            'shipping_address': shipping_address,
            'billing_address': billing_address,
        }
        return result

    @staticmethod
    def validate_password_strength(password: str, password_service=None) -> Result:
        result = Result()
        service = AuthController._get_service('password_service', password_service)
        if not service:
            return AuthController._service_unavailable_result('Password service not available')

        result.data = service.validate_password_strength(password)
        return result
