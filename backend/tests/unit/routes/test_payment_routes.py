"""
Unit tests for payment processing routes and PaymentService.
Uses mocked Square adapter so no real API calls are made.
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from server.services.payment_service import PaymentService
from server.thirdparty.square import SquareAdapter


PAYMENT_PAYLOAD = {
    "amount": 1999,
    "currency": "USD",
    "source_id": "cnon:card-nonce-ok",
    "buyer_email": "buyer@example.com",
    "order_id": "order_001",
}


def _auth_headers(token="tok123"):
    return {"Authorization": f"Bearer {token}", "X-CSRF-Token": token}


# ---------------------------------------------------------------------------
# PaymentService unit tests (no HTTP)
# ---------------------------------------------------------------------------

class TestPaymentService:
    @pytest.fixture
    def mock_square(self):
        adapter = MagicMock(spec=SquareAdapter)
        adapter.is_configured = True
        return adapter

    @pytest.fixture
    def payment_service(self, mock_square):
        return PaymentService(mock_square)

    def test_process_payment_success(self, payment_service, mock_square):
        mock_square.process_payment.return_value = {
            "success": True,
            "payment_id": "pay_abc",
            "status": "COMPLETED",
            "amount": 1999,
            "currency": "USD",
        }
        result = payment_service.process_payment(
            amount=1999,
            source_id="cnon:card-nonce-ok",
            order_id="order_001",
        )
        assert result["success"] is True
        assert result["payment_id"] == "pay_abc"
        mock_square.process_payment.assert_called_once()

    def test_process_payment_failure_propagates_error(self, payment_service, mock_square):
        mock_square.process_payment.return_value = {
            "success": False,
            "error": "Card declined",
            "payment_id": None,
        }
        result = payment_service.process_payment(amount=1999, source_id="bad-nonce")
        assert result["success"] is False
        assert "error" in result

    def test_process_payment_missing_source_id(self, payment_service, mock_square):
        mock_square.process_payment.return_value = {
            "success": False,
            "error": "Payment source ID is required",
            "payment_id": None,
        }
        result = payment_service.process_payment(amount=500, source_id=None)
        assert result["success"] is False

    def test_get_payment_success(self, payment_service, mock_square):
        mock_square.get_payment.return_value = {
            "success": True,
            "payment": {"id": "pay_abc", "status": "COMPLETED"},
        }
        result = payment_service.get_payment("pay_abc")
        assert result["success"] is True

    def test_refund_payment_success(self, payment_service, mock_square):
        mock_square.refund_payment.return_value = {
            "success": True,
            "refund_id": "ref_001",
        }
        result = payment_service.refund_payment("pay_abc", amount=1999)
        assert result["success"] is True


# ---------------------------------------------------------------------------
# Webhook signature validation (unit)
# ---------------------------------------------------------------------------

class TestWebhookSignatureValidation:
    def test_rejects_when_signature_key_missing(self):
        adapter = SquareAdapter.__new__(SquareAdapter)
        adapter.client = None
        with patch.dict("os.environ", {}, clear=False):
            import os
            os.environ.pop("SQUARE_WEBHOOK_SIGNATURE_KEY", None)
            result = adapter.validate_webhook_signature(
                payload='{"type":"payment.completed"}',
                signature="some_signature",
                webhook_url="https://example.com/api/payments/webhook",
            )
        assert result is False

    def test_accepts_valid_hmac_signature(self):
        import hmac as _hmac
        import hashlib
        import base64

        key = "test_webhook_key"
        url = "https://example.com/api/payments/webhook"
        body = '{"type":"payment.completed"}'
        message = (url + body).encode("utf-8")
        sig = base64.b64encode(
            _hmac.new(key.encode("utf-8"), message, hashlib.sha256).digest()
        ).decode("utf-8")

        adapter = SquareAdapter.__new__(SquareAdapter)
        with patch.dict("os.environ", {"SQUARE_WEBHOOK_SIGNATURE_KEY": key}):
            result = adapter.validate_webhook_signature(
                payload=body, signature=sig, webhook_url=url
            )
        assert result is True

    def test_rejects_tampered_payload(self):
        import hmac as _hmac
        import hashlib
        import base64

        key = "test_webhook_key"
        url = "https://example.com/api/payments/webhook"
        original_body = '{"type":"payment.completed"}'
        tampered_body = '{"type":"payment.completed","amount":0}'

        message = (url + original_body).encode("utf-8")
        sig = base64.b64encode(
            _hmac.new(key.encode("utf-8"), message, hashlib.sha256).digest()
        ).decode("utf-8")

        adapter = SquareAdapter.__new__(SquareAdapter)
        with patch.dict("os.environ", {"SQUARE_WEBHOOK_SIGNATURE_KEY": key}):
            result = adapter.validate_webhook_signature(
                payload=tampered_body, signature=sig, webhook_url=url
            )
        assert result is False


# ---------------------------------------------------------------------------
# Payment route auth protection
# ---------------------------------------------------------------------------

class TestPaymentRouteProtection:
    """Payment routes that require authentication should reject unauthenticated requests."""

    def test_process_payment_requires_auth(self, client):
        resp = client.post(
            "/api/payments/",
            data=json.dumps(PAYMENT_PAYLOAD),
            content_type="application/json",
        )
        assert resp.status_code in (401, 403)

    def test_get_payment_requires_auth(self, client):
        resp = client.get("/api/payments/pay_test_123")
        assert resp.status_code in (401, 403)

    def test_refund_requires_admin_role(self, client):
        resp = client.post(
            "/api/payments/pay_test_123/refund",
            data=json.dumps({"amount": 100, "reason": "test"}),
            content_type="application/json",
        )
        assert resp.status_code in (401, 403)
