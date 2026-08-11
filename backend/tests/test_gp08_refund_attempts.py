"""GP-08 durable refund reservation and reconciliation tests."""

from decimal import Decimal
from unittest.mock import Mock

from server.config import database as db
from server.models.order import (
    Order, OrderStatus, Payment, PaymentStatus, Refund, RefundAttempt,
)
from server.services.refund_service import RefundService
from server.routes.payment_routes import _handle_square_webhook_event


def _paid_order():
    order = Order(
        order_number="GP08-ORDER-1",
        customer_email="buyer@example.test",
        customer_first_name="Test",
        customer_last_name="Buyer",
        status=OrderStatus.PROCESSING,
        subtotal=Decimal("10.00"),
        shipping_cost=Decimal("0.00"),
        tax_amount=Decimal("0.00"),
        total_amount=Decimal("10.00"),
        currency="USD",
        shipping_address={"country": "US"},
        billing_address={"country": "US"},
        payment_status=PaymentStatus.COMPLETED,
        payment_provider="square",
        payment_id="sq-payment-gp08",
    )
    db.session.add(order)
    db.session.flush()
    payment = Payment(
        order_id=order.id,
        payment_provider="square",
        external_payment_id="sq-payment-gp08",
        amount=Decimal("10.00"),
        currency="USD",
        status=PaymentStatus.COMPLETED,
    )
    db.session.add(payment)
    db.session.commit()
    return order, payment


def _service(results):
    provider = Mock()
    provider.refund_payment.side_effect = results
    return RefundService(provider), provider


def _success(refund_id):
    return {
        "success": True,
        "refund_id": refund_id,
        "payment_id": "sq-payment-gp08",
        "amount": 400,
        "status": "COMPLETED",
    }


def test_partial_then_full_refund_uses_distinct_durable_keys(app):
    with app.app_context():
        order, _payment = _paid_order()
        service, provider = _service([_success("sq-refund-1"), _success("sq-refund-2")])

        partial = service.process_refund(order.id, 400, "partial")
        final = service.process_refund(order.id, 600, "remainder")

        assert partial["success"] is True
        assert final["success"] is True
        assert Refund.query.count() == 2
        assert RefundAttempt.query.count() == 2
        keys = [call.kwargs["idempotency_key"] for call in provider.refund_payment.call_args_list]
        assert len(set(keys)) == 2
        assert Payment.query.one().status == PaymentStatus.REFUNDED
        assert Order.query.one().status == OrderStatus.REFUNDED


def test_cumulative_over_refund_is_rejected_before_provider(app):
    with app.app_context():
        order, payment = _paid_order()
        db.session.add(
            Refund(
                order_id=order.id,
                payment_id=payment.id,
                refund_amount=Decimal("8.00"),
                currency="USD",
                external_refund_id="existing-refund",
            )
        )
        db.session.commit()
        service, provider = _service([])

        result = service.process_refund(order.id, 300, "too much")

        assert result["success"] is False
        assert result["code"] == "REFUND_EXCEEDS_CHARGE"
        provider.refund_payment.assert_not_called()


def test_unknown_refund_retries_same_request_with_same_key(app):
    with app.app_context():
        order, _payment = _paid_order()
        service, provider = _service(
            [
                {
                    "success": False,
                    "outcome_known": False,
                    "error": "response lost",
                },
                _success("sq-refund-retried"),
            ]
        )

        first = service.process_refund(order.id, 400, "same request")
        stable_key = RefundAttempt.query.one().idempotency_key
        second = service.process_refund(order.id, 400, "same request")

        assert first["success"] is False
        assert second["success"] is True
        assert {
            call.kwargs["idempotency_key"] for call in provider.refund_payment.call_args_list
        } == {stable_key}
        assert Refund.query.count() == 1


def test_unknown_refund_blocks_changed_amount(app):
    with app.app_context():
        order, _payment = _paid_order()
        service, provider = _service(
            [{"success": False, "outcome_known": False, "error": "response lost"}]
        )

        service.process_refund(order.id, 400, "same request")
        changed = service.process_refund(order.id, 500, "same request")

        assert changed["success"] is False
        assert changed["code"] == "REFUND_RECONCILIATION_PENDING"
        assert provider.refund_payment.call_count == 1


def test_webhook_reconciles_unknown_refund_without_second_provider_call(app):
    with app.app_context():
        order, payment = _paid_order()
        attempt = RefundAttempt(
            order_id=order.id,
            payment_id=payment.id,
            provider="square",
            idempotency_key="gp08-unknown-refund-key",
            amount_cents=400,
            currency="USD",
            reason="unknown response",
            status="unknown",
        )
        db.session.add(attempt)
        db.session.commit()

        _handle_square_webhook_event(
            "refund.updated",
            {
                "refund": {
                    "id": "sq-refund-webhook",
                    "payment_id": payment.external_payment_id,
                    "status": "COMPLETED",
                    "amount_money": {"amount": 400, "currency": "USD"},
                    "reason": "unknown response",
                }
            },
        )
        db.session.commit()

        assert Refund.query.filter_by(external_refund_id="sq-refund-webhook").count() == 1
        assert RefundAttempt.query.filter_by(id=attempt.id).one().status == "succeeded"
        assert Payment.query.filter_by(id=payment.id).one().status == PaymentStatus.PARTIALLY_REFUNDED
