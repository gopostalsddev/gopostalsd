"""Regression tests to ensure marshalled routes preserve structured error payloads."""

import json
from unittest.mock import Mock, patch

from server.controllers.helpers import Result


class TestMarshalledErrorEnvelope:
    def test_pricing_options_controller_error_returns_structured_error(self, client):
        with patch("server.routes.pricing_routes.PricingController.get_product_options") as mock_controller:
            mock_controller.return_value = Result(status=False, error="Controller Error")

            response = client.get("/api/pricing/products/123/options?store_code=6")

            assert response.status_code == 400
            payload = json.loads(response.data)
            assert payload["error"]["message"] == "Controller Error"
            assert payload["error"]["code"] == "PRICING_OPTIONS_ERROR"
            assert payload["error"]["category"] == "business_logic"

    def test_auth_refresh_missing_token_returns_structured_error(self, client):
        response = client.post("/api/auth/refresh", json={})

        assert response.status_code == 400
        payload = json.loads(response.data)
        assert payload["error"]["message"] == "Refresh token is required"
        assert payload["error"]["code"] == "BAD_REQUEST"
        assert payload["error"]["category"] == "validation"

    def test_order_payment_error_returns_structured_error(self, client):
        mock_service = Mock()
        mock_service.process_payment.return_value = {
            "success": False,
            "error": "Payment failed",
        }

        admin_user = Mock()
        admin_user.id = 1
        admin_user.is_active.return_value = True
        admin_user.role = Mock()
        admin_user.role.name = "Admin"

        auth_service = Mock()
        auth_service.get_user_by_session.return_value = admin_user

        client.application.extensions["auth_service"] = auth_service

        with patch("server.routes.order_routes.get_order_service", return_value=mock_service):
            response = client.post(
                "/api/orders/1/payment",
                json={"source_id": "src_123"},
                headers={
                    "Authorization": "Bearer test-session",
                    "X-CSRF-Token": "test-session",
                },
            )

            assert response.status_code == 400
            payload = json.loads(response.data)
            assert payload["error"]["message"] == "Payment failed"
            assert payload["error"]["code"] == "ORDER_PAYMENT_ERROR"
            assert payload["error"]["category"] == "business_logic"
