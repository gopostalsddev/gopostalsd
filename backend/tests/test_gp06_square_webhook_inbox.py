"""GP-06 durable inbox, replay, and retry contract tests."""

import json
from unittest.mock import patch

from server.models.webhook import SquareWebhookReceipt


WEBHOOK_URL = "https://payments.example.test/api/payments/webhook"


class _AcceptingPaymentService:
    is_configured = True

    def validate_webhook(self, payload, signature, webhook_url):
        return signature == "valid" and webhook_url == WEBHOOK_URL


def _post(client, event):
    return client.post(
        "/api/payments/webhook",
        data=json.dumps(event, separators=(",", ":")).encode(),
        content_type="application/json",
        headers={"x-square-hmacsha256-signature": "valid"},
    )


def _event(event_id="evt-gp06-1", amount=100):
    return {
        "event_id": event_id,
        "type": "payment.updated",
        "data": {"object": {"payment": {"id": "pay-1", "amount": amount}}},
    }


def _route_context():
    return (
        patch.dict("os.environ", {"SQUARE_WEBHOOK_URL": WEBHOOK_URL}, clear=False),
        patch(
            "server.routes.payment_routes.PaymentService",
            return_value=_AcceptingPaymentService(),
        ),
    )


def test_success_is_persisted_and_duplicate_is_not_reprocessed(client, app):
    env_patch, service_patch = _route_context()
    with env_patch, service_patch, patch(
        "server.routes.payment_routes._handle_square_webhook_event"
    ) as handler:
        first = _post(client, _event())
        duplicate = _post(client, _event())

    assert first.status_code == 200
    assert first.get_json() == {"status": "success"}
    assert duplicate.status_code == 200
    assert duplicate.get_json() == {"status": "duplicate"}
    handler.assert_called_once()

    with app.app_context():
        receipt = SquareWebhookReceipt.query.filter_by(event_id="evt-gp06-1").one()
        assert receipt.status == "processed"
        assert receipt.attempts == 1
        assert receipt.processed_at is not None


def test_processing_failure_is_durable_and_retried(client, app):
    env_patch, service_patch = _route_context()
    with env_patch, service_patch, patch(
        "server.routes.payment_routes._handle_square_webhook_event",
        side_effect=(RuntimeError("provider state unavailable"), None),
    ) as handler:
        failed = _post(client, _event("evt-retry"))
        retried = _post(client, _event("evt-retry"))

    assert failed.status_code == 503
    assert retried.status_code == 200
    assert handler.call_count == 2

    with app.app_context():
        receipt = SquareWebhookReceipt.query.filter_by(event_id="evt-retry").one()
        assert receipt.status == "processed"
        assert receipt.attempts == 2
        assert receipt.last_error_code is None


def test_reused_event_id_with_different_payload_is_rejected(client):
    env_patch, service_patch = _route_context()
    with env_patch, service_patch, patch(
        "server.routes.payment_routes._handle_square_webhook_event"
    ) as handler:
        assert _post(client, _event("evt-conflict", amount=100)).status_code == 200
        conflict = _post(client, _event("evt-conflict", amount=200))

    assert conflict.status_code == 409
    assert handler.call_count == 1


def test_missing_event_identity_is_rejected_before_inbox_write(client, app):
    env_patch, service_patch = _route_context()
    with env_patch, service_patch:
        response = _post(client, {"type": "payment.updated", "data": {}})

    assert response.status_code == 400
    with app.app_context():
        assert SquareWebhookReceipt.query.count() == 0

