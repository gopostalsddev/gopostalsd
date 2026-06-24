"""
Unit tests for authentication routes.
Covers register, login, verify-email, resend-verification, and password-reset endpoints.
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from server.controllers.helpers import Result


REGISTER_PAYLOAD = {
    "email": "test@example.com",
    "password": "SecurePass1!",
    "first_name": "Jane",
    "last_name": "Doe",
    "shipping_address": {
        "street": "123 Main St",
        "city": "San Diego",
        "state": "CA",
        "zip_code": "92101",
        "country": "US",
    },
}

LOGIN_PAYLOAD = {
    "email": "test@example.com",
    "password": "SecurePass1!",
}


def _ok_result(data=None):
    r = Result()
    r.status = True
    r.data = data or {"message": "ok"}
    return r


def _fail_result(error="Error"):
    r = Result()
    r.status = False
    r.error = error
    r.details = "TEST_ERROR"
    return r


# ---------------------------------------------------------------------------
# POST /api/auth/register
# ---------------------------------------------------------------------------

class TestRegisterRoute:
    def test_missing_body_returns_400(self, client):
        resp = client.post("/api/auth/register", content_type="application/json")
        assert resp.status_code == 400

    def test_invalid_email_returns_400(self, client):
        payload = {**REGISTER_PAYLOAD, "email": "not-an-email"}
        resp = client.post(
            "/api/auth/register",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_missing_address_returns_400(self, client):
        payload = {**REGISTER_PAYLOAD}
        del payload["shipping_address"]
        resp = client.post(
            "/api/auth/register",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_successful_registration(self, client):
        with patch("server.routes.auth_routes.AuthController.register_user") as mock_reg:
            mock_reg.return_value = _ok_result({"user": {"id": 1, "email": "test@example.com"}})
            resp = client.post(
                "/api/auth/register",
                data=json.dumps(REGISTER_PAYLOAD),
                content_type="application/json",
            )
        assert resp.status_code == 201

    def test_registration_service_error_returns_400(self, client):
        with patch("server.routes.auth_routes.AuthController.register_user") as mock_reg:
            mock_reg.return_value = _fail_result("Email already exists")
            resp = client.post(
                "/api/auth/register",
                data=json.dumps(REGISTER_PAYLOAD),
                content_type="application/json",
            )
        assert resp.status_code == 400
        data = resp.get_json()
        assert "error" in data or "message" in str(data)


# ---------------------------------------------------------------------------
# POST /api/auth/login
# ---------------------------------------------------------------------------

class TestLoginRoute:
    def test_missing_body_returns_400(self, client):
        resp = client.post("/api/auth/login", content_type="application/json")
        assert resp.status_code == 400

    def test_missing_password_returns_400(self, client):
        resp = client.post(
            "/api/auth/login",
            data=json.dumps({"email": "test@example.com"}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_invalid_email_format_returns_400(self, client):
        resp = client.post(
            "/api/auth/login",
            data=json.dumps({"email": "bad", "password": "pass"}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_failed_login_returns_401(self, client):
        with patch("server.routes.auth_routes.AuthController.login") as mock_login:
            mock_login.return_value = _fail_result("Invalid credentials")
            resp = client.post(
                "/api/auth/login",
                data=json.dumps(LOGIN_PAYLOAD),
                content_type="application/json",
            )
        assert resp.status_code == 401

    def test_successful_login_returns_200(self, client):
        session_data = {
            "user": {"id": 1, "email": "test@example.com", "role": "RegisteredCustomer"},
            "session": {
                "session_token": "tok123",
                "refresh_token": "ref456",
                "expires_at": "2030-01-01T00:00:00",
            },
        }
        with patch("server.routes.auth_routes.AuthController.login") as mock_login:
            mock_login.return_value = _ok_result(session_data)
            resp = client.post(
                "/api/auth/login",
                data=json.dumps(LOGIN_PAYLOAD),
                content_type="application/json",
            )
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# POST /api/auth/verify-email
# ---------------------------------------------------------------------------

class TestVerifyEmailRoute:
    def test_missing_token_returns_400(self, client):
        resp = client.post(
            "/api/auth/verify-email",
            data=json.dumps({}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_invalid_token_returns_400(self, client):
        with patch("server.routes.auth_routes.AuthController.verify_email") as mock_verify:
            mock_verify.return_value = _fail_result("Invalid token")
            resp = client.post(
                "/api/auth/verify-email",
                data=json.dumps({"token": "badtoken"}),
                content_type="application/json",
            )
        assert resp.status_code == 400

    def test_valid_token_returns_200(self, client):
        with patch("server.routes.auth_routes.AuthController.verify_email") as mock_verify:
            mock_verify.return_value = _ok_result({"message": "Email verified"})
            resp = client.post(
                "/api/auth/verify-email",
                data=json.dumps({"token": "validtoken123"}),
                content_type="application/json",
            )
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# POST /api/auth/resend-verification
# ---------------------------------------------------------------------------

class TestResendVerificationRoute:
    def test_missing_email_returns_400(self, client):
        resp = client.post(
            "/api/auth/resend-verification",
            data=json.dumps({}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_invalid_email_returns_400(self, client):
        resp = client.post(
            "/api/auth/resend-verification",
            data=json.dumps({"email": "notvalid"}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_valid_email_returns_200(self, client):
        with patch("server.routes.auth_routes.AuthController.resend_verification_email") as mock_resend:
            mock_resend.return_value = _ok_result({"message": "Email sent"})
            resp = client.post(
                "/api/auth/resend-verification",
                data=json.dumps({"email": "user@example.com"}),
                content_type="application/json",
            )
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# POST /api/auth/password-reset/request
# ---------------------------------------------------------------------------

class TestPasswordResetRequestRoute:
    def test_missing_email_returns_400(self, client):
        resp = client.post(
            "/api/auth/password-reset/request",
            data=json.dumps({}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_valid_request_returns_200(self, client):
        with patch("server.routes.auth_routes.AuthController.request_password_reset") as mock_reset:
            mock_reset.return_value = _ok_result({"message": "Reset email sent"})
            resp = client.post(
                "/api/auth/password-reset/request",
                data=json.dumps({"email": "user@example.com"}),
                content_type="application/json",
            )
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Admin route protection
# ---------------------------------------------------------------------------

class TestAdminRouteProtection:
    """Admin endpoints must return 401/403 without a valid Admin session."""

    def test_product_sync_without_auth_returns_401(self, client):
        resp = client.post("/api/print/categories/1/sync-products")
        assert resp.status_code in (401, 403)

    def test_category_sync_without_auth_returns_401(self, client):
        resp = client.post("/api/print/categories/sync")
        assert resp.status_code in (401, 403)

    def test_product_create_without_auth_returns_401(self, client):
        resp = client.post(
            "/api/print/products",
            data=json.dumps({"name": "x", "sku": "y", "category_id": 1, "vendor_id": 1}),
            content_type="application/json",
        )
        assert resp.status_code in (401, 403)
