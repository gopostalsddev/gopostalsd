"""GP-07 durable payment attempt and stable-idempotency tests."""

from decimal import Decimal
from unittest.mock import Mock

from server.config import database as db
from server.models.order import (
    Order, OrderStatus, Payment, PaymentAttempt, PaymentStatus,
)
from server.services.order_service import OrderService
from server.routes.payment_routes import _handle_square_webhook_event


def _order():
    row = Order(
        order_number="GP07-ORDER-1",
        customer_email="buyer@example.test",
        customer_first_name="Test",
        customer_last_name="Buyer",
        status=OrderStatus.PENDING,
        subtotal=Decimal("10.00"),
        shipping_cost=Decimal("0.00"),
        tax_amount=Decimal("0.00"),
        total_amount=Decimal("10.00"),
        currency="USD",
        shipping_address={"country": "US"},
        billing_address={"country": "US"},
        payment_status=PaymentStatus.PENDING,
    )
    db.session.add(row)
    db.session.commit()
    return row


def _service(results):
    payment = Mock()
    payment.provider = "square"
    payment.process_payment.side_effect = results
    return OrderService(payment, Mock()), payment


def _success(payment_id="sq-payment-1"):
    return {
        "success": True,
        "payment_id": payment_id,
        "status": "COMPLETED",
        "amount": 1000,
        "currency": "USD",
    }


def test_attempt_is_committed_before_provider_and_success_replays_locally(app):
    with app.app_context():
        order = _order()
        observed = {}

        def provider_result(**kwargs):
            attempt = PaymentAttempt.query.filter_by(order_id=order.id).one()
            observed["status"] = attempt.status
            observed["key"] = attempt.idempotency_key
            observed["reference"] = attempt.provider_reference
            return _success()

        service, provider = _service([])
        provider.process_payment.side_effect = provider_result
        first = service.process_payment(order.id, {"source_id": "card-token-1"})
        second = service.process_payment(order.id, {"source_id": "card-token-1"})

        assert first["success"] is True
        assert second["success"] is True
        assert provider.process_payment.call_count == 1
        assert observed["status"] == "processing"
        assert provider.process_payment.call_args.kwargs["idempotency_key"] == observed["key"]
        assert provider.process_payment.call_args.kwargs["reference_id"] == observed["reference"]
        assert PaymentAttempt.query.one().status == "succeeded"
        assert Payment.query.count() == 1


def test_unknown_outcome_retries_same_source_with_same_provider_key(app):
    with app.app_context():
        order = _order()
        service, provider = _service(
            [
                {
                    "success": False,
                    "payment_id": None,
                    "outcome_known": False,
                    "error": "temporary transport error",
                },
                _success(),
            ]
        )

        first = service.process_payment(order.id, {"source_id": "card-token-1"})
        attempt = PaymentAttempt.query.one()
        stable_key = attempt.idempotency_key
        second = service.process_payment(order.id, {"source_id": "card-token-1"})

        assert first["success"] is False
        assert second["success"] is True
        assert provider.process_payment.call_count == 2
        assert {
            call.kwargs["idempotency_key"] for call in provider.process_payment.call_args_list
        } == {stable_key}
        assert PaymentAttempt.query.count() == 1


def test_unknown_outcome_rejects_different_source_without_provider_call(app):
    with app.app_context():
        order = _order()
        service, provider = _service(
            [
                {
                    "success": False,
                    "payment_id": None,
                    "outcome_known": False,
                    "error": "temporary transport error",
                }
            ]
        )

        service.process_payment(order.id, {"source_id": "card-token-1"})
        result = service.process_payment(order.id, {"source_id": "different-token"})

        assert result["success"] is False
        assert "reconciled" in result["error"]
        assert provider.process_payment.call_count == 1


def test_definitive_decline_allows_new_attempt_with_new_key(app):
    with app.app_context():
        order = _order()
        service, provider = _service(
            [
                {
                    "success": False,
                    "payment_id": None,
                    "outcome_known": True,
                    "error": "Payment was declined",
                },
                _success(),
            ]
        )

        declined = service.process_payment(order.id, {"source_id": "card-token-1"})
        accepted = service.process_payment(order.id, {"source_id": "card-token-2"})

        assert declined["success"] is False
        assert accepted["success"] is True
        keys = [call.kwargs["idempotency_key"] for call in provider.process_payment.call_args_list]
        assert len(set(keys)) == 2
        assert PaymentAttempt.query.count() == 2
        assert [row.status for row in PaymentAttempt.query.order_by(PaymentAttempt.id)] == [
            "failed", "succeeded"
        ]


def test_provider_exception_becomes_unknown_and_keeps_stable_attempt(app):
    with app.app_context():
        order = _order()
        service, provider = _service([TimeoutError("response lost")])

        result = service.process_payment(order.id, {"source_id": "card-token-1"})

        assert result["success"] is False
        assert PaymentAttempt.query.one().status == "unknown"
        assert Order.query.get(order.id).payment_status == PaymentStatus.PROCESSING
        assert provider.process_payment.call_count == 1


def test_webhook_before_response_reconciles_attempt_by_safe_reference(app):
    with app.app_context():
        order = _order()
        attempt = PaymentAttempt(
            order_id=order.id,
            provider="square",
            idempotency_key="gp07-webhook-key",
            provider_reference="gp-1-webhook-reference",
            source_fingerprint="a" * 64,
            amount_cents=1000,
            currency="USD",
            status="processing",
        )
        db.session.add(attempt)
        db.session.commit()

        _handle_square_webhook_event(
            "payment.updated",
            {
                "payment": {
                    "id": "sq-webhook-payment",
                    "status": "COMPLETED",
                    "reference_id": attempt.provider_reference,
                    "amount_money": {"amount": 1000, "currency": "USD"},
                }
            },
        )
        db.session.commit()

        assert Payment.query.filter_by(external_payment_id="sq-webhook-payment").count() == 1
        assert PaymentAttempt.query.get(attempt.id).status == "succeeded"
        assert Order.query.get(order.id).payment_status == PaymentStatus.COMPLETED
