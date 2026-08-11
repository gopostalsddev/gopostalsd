"""GP-05 tests for Square's exact URL and raw-body signature contract."""

import base64
import hashlib
import hmac
from unittest.mock import patch

import pytest

from server.square_config import SquareConfigurationError, square_webhook_url
from server.thirdparty.square import SquareAdapter


WEBHOOK_URL = "https://payments.example.test/api/payments/webhook"
SIGNATURE_KEY = "gp05-test-signature-key"
BODY = b'{\n  "event_id": "gp05-event-1", "type": "payment.updated", "data": {"object": {}}\n}'


def _signature(body=BODY, url=WEBHOOK_URL):
    return base64.b64encode(
        hmac.new(
            SIGNATURE_KEY.encode(), url.encode() + body, hashlib.sha256
        ).digest()
    ).decode()


@pytest.mark.parametrize(
    "value",
    (
        "",
        "http://payments.example.test/api/payments/webhook",
        "https://payments.example.test",
        "https://payments.example.test/api/payments/webhook/",
        "https://payments.example.test/api/payments/webhook?source=square",
        "https://payments.example.test/api/payments/webhook#fragment",
        "https://user:password@payments.example.test/api/payments/webhook",
    ),
)
def test_canonical_url_rejects_missing_base_or_derived_variants(value):
    with pytest.raises(SquareConfigurationError):
        square_webhook_url({"SQUARE_WEBHOOK_URL": value})


def test_signature_uses_exact_url_and_unmodified_raw_body():
    adapter = SquareAdapter.__new__(SquareAdapter)
    with patch.dict(
        "os.environ", {"SQUARE_WEBHOOK_SIGNATURE_KEY": SIGNATURE_KEY}, clear=False
    ):
        signature = _signature()
        assert adapter.validate_webhook_signature(BODY, signature, WEBHOOK_URL)
        assert not adapter.validate_webhook_signature(
            BODY.replace(b"  ", b" "), signature, WEBHOOK_URL
        )
        assert not adapter.validate_webhook_signature(
            BODY, signature, WEBHOOK_URL + "/"
        )


class _FakePaymentService:
    expected_signature = _signature()
    calls = []

    @property
    def is_configured(self):
        return True

    def validate_webhook(self, payload, signature, webhook_url):
        self.calls.append((payload, signature, webhook_url))
        return signature == self.expected_signature


def test_route_accepts_official_header_and_passes_raw_bytes(client):
    _FakePaymentService.calls.clear()
    with (
        patch.dict("os.environ", {"SQUARE_WEBHOOK_URL": WEBHOOK_URL}, clear=False),
        patch(
            "server.routes.payment_routes.PaymentService",
            return_value=_FakePaymentService(),
        ),
        patch("server.routes.payment_routes._handle_square_webhook_event"),
    ):
        response = client.post(
            "/api/payments/webhook",
            data=BODY,
            content_type="application/json",
            headers={
                "x-square-hmacsha256-signature": _signature(),
                "Host": "attacker.invalid",
            },
        )

    assert response.status_code == 200
    assert _FakePaymentService.calls == [(BODY, _signature(), WEBHOOK_URL)]


def test_obsolete_header_is_not_accepted(client):
    _FakePaymentService.calls.clear()
    with (
        patch.dict("os.environ", {"SQUARE_WEBHOOK_URL": WEBHOOK_URL}, clear=False),
        patch(
            "server.routes.payment_routes.PaymentService",
            return_value=_FakePaymentService(),
        ),
    ):
        response = client.post(
            "/api/payments/webhook",
            data=BODY,
            content_type="application/json",
            headers={"X-Square-Signature": _signature()},
        )

    assert response.status_code == 401
    assert _FakePaymentService.calls == [(BODY, "", WEBHOOK_URL)]


def test_missing_canonical_url_fails_before_service_initialization(client):
    with (
        patch.dict("os.environ", {}, clear=False),
        patch("server.routes.payment_routes.PaymentService") as payment_service,
    ):
        import os

        os.environ.pop("SQUARE_WEBHOOK_URL", None)
        response = client.post(
            "/api/payments/webhook",
            data=BODY,
            content_type="application/json",
            headers={"x-square-hmacsha256-signature": _signature()},
        )

    assert response.status_code == 500
    payment_service.assert_not_called()
