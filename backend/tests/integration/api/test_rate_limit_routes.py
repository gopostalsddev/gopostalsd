"""Integration tests for per-IP rate limiting on abuse-prone endpoints."""

from server.middleware import rate_limit_middleware


def _assert_rate_limited(response):
    assert response.status_code == 429
    payload = response.get_json()
    assert payload["error"]["code"] == "RATE_LIMIT_EXCEEDED"
    assert payload["error"]["category"] == "security"


class TestRateLimitRoutes:
    def setup_method(self):
        rate_limit_middleware.reset_rate_limit_state()

    def teardown_method(self):
        rate_limit_middleware.reset_rate_limit_state()

    def test_login_route_rate_limited_per_ip(self, client):
        app = client.application
        app.config.update(
            AUTH_RATE_LIMIT_ENABLED=True,
            AUTH_RATE_LIMIT_STORE="memory",
            AUTH_LOGIN_RATE_LIMIT_COUNT=2,
            AUTH_LOGIN_RATE_LIMIT_WINDOW_SECONDS=60,
        )

        payload = {"email": "invalid-email", "password": "password"}
        headers = {"X-Forwarded-For": "203.0.113.10"}

        first = client.post("/api/auth/login", json=payload, headers=headers)
        second = client.post("/api/auth/login", json=payload, headers=headers)
        third = client.post("/api/auth/login", json=payload, headers=headers)

        assert first.status_code == 400
        assert second.status_code == 400
        _assert_rate_limited(third)

    def test_register_route_rate_limited_per_ip(self, client):
        app = client.application
        app.config.update(
            AUTH_RATE_LIMIT_ENABLED=True,
            AUTH_RATE_LIMIT_STORE="memory",
            AUTH_REGISTER_RATE_LIMIT_COUNT=2,
            AUTH_REGISTER_RATE_LIMIT_WINDOW_SECONDS=60,
        )

        payload = {
            "email": "invalid-email",
            "password": "StrongPass123!",
            "first_name": "Test",
            "last_name": "User",
            "shipping_address": {
                "street": "123 Main",
                "city": "San Diego",
                "state": "CA",
                "zip_code": "92101",
                "country": "US",
            },
        }
        headers = {"X-Forwarded-For": "203.0.113.11"}

        first = client.post("/api/auth/register", json=payload, headers=headers)
        second = client.post("/api/auth/register", json=payload, headers=headers)
        third = client.post("/api/auth/register", json=payload, headers=headers)

        assert first.status_code == 400
        assert second.status_code == 400
        _assert_rate_limited(third)

    def test_password_reset_request_route_rate_limited_per_ip(self, client):
        app = client.application
        app.config.update(
            AUTH_RATE_LIMIT_ENABLED=True,
            AUTH_RATE_LIMIT_STORE="memory",
            AUTH_PASSWORD_RESET_RATE_LIMIT_COUNT=2,
            AUTH_PASSWORD_RESET_RATE_LIMIT_WINDOW_SECONDS=60,
        )

        payload = {"email": "invalid-email"}
        headers = {"X-Forwarded-For": "203.0.113.12"}

        first = client.post("/api/auth/password-reset/request", json=payload, headers=headers)
        second = client.post("/api/auth/password-reset/request", json=payload, headers=headers)
        third = client.post("/api/auth/password-reset/request", json=payload, headers=headers)

        assert first.status_code == 400
        assert second.status_code == 400
        _assert_rate_limited(third)

    def test_contact_route_rate_limited_per_ip(self, client):
        app = client.application
        app.config.update(
            AUTH_RATE_LIMIT_ENABLED=True,
            AUTH_RATE_LIMIT_STORE="memory",
            CONTACT_RATE_LIMIT_COUNT=2,
            CONTACT_RATE_LIMIT_WINDOW_SECONDS=60,
        )

        payload = {
            "name": "Rate Limit Test",
            "email": "invalid-email",
            "subject": "Hello",
            "message": "Testing",
        }
        headers = {"X-Forwarded-For": "203.0.113.13"}

        first = client.post("/api/contact/", json=payload, headers=headers)
        second = client.post("/api/contact/", json=payload, headers=headers)
        third = client.post("/api/contact/", json=payload, headers=headers)

        assert first.status_code == 400
        assert second.status_code == 400
        _assert_rate_limited(third)
