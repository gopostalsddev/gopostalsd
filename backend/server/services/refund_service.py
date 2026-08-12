"""Canonical durable refund lifecycle."""

from datetime import datetime, timezone
from decimal import Decimal
import logging
import uuid

from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from server.config import database as db
from server.models.order import (
    Order, OrderStatus, Payment, PaymentStatus, Refund, RefundAttempt,
)


logger = logging.getLogger(__name__)


class RefundService:
    def __init__(self, payment_service):
        self.payment_service = payment_service

    def process_refund(self, order_id, amount_cents, reason=None, external_payment_id=None):
        attempt_id = None
        try:
            order = Order.query.with_for_update().filter_by(id=order_id).first()
            if not order:
                return {"success": False, "error": "Order not found", "code": "ORDER_NOT_FOUND"}

            payment_query = Payment.query.with_for_update().filter_by(order_id=order.id)
            if external_payment_id:
                payment_query = payment_query.filter_by(external_payment_id=external_payment_id)
            payment = payment_query.order_by(Payment.id.desc()).first()
            if not payment:
                return {"success": False, "error": "No matching payment record found", "code": "PAYMENT_ID_NOT_FOUND"}

            normalized_reason = (reason or "Customer requested refund").strip()
            active = (
                RefundAttempt.query.with_for_update()
                .filter(
                    RefundAttempt.payment_id == payment.id,
                    RefundAttempt.status.in_(("reserved", "processing", "unknown")),
                )
                .order_by(RefundAttempt.id.desc())
                .first()
            )
            if active:
                if active.amount_cents != amount_cents or active.reason != normalized_reason:
                    return {
                        "success": False,
                        "error": "A refund is already being reconciled for this payment",
                        "code": "REFUND_RECONCILIATION_PENDING",
                    }
                if active.status == "processing":
                    return {
                        "success": False,
                        "error": "Refund processing is already in progress",
                        "code": "REFUND_IN_PROGRESS",
                    }
                attempt = active
                attempt.status = "processing"
                attempt.last_error_code = None
            else:
                committed = db.session.query(
                    func.coalesce(func.sum(Refund.refund_amount), 0)
                ).filter_by(payment_id=payment.id).scalar()
                committed_cents = int(Decimal(str(committed)) * 100)
                payment_cents = int(Decimal(str(payment.amount)) * 100)
                if committed_cents + amount_cents > payment_cents:
                    return {
                        "success": False,
                        "error": f"Refund exceeds remaining balance ({payment_cents - committed_cents} cents)",
                        "code": "REFUND_EXCEEDS_CHARGE",
                    }
                attempt = RefundAttempt(
                    order_id=order.id,
                    payment_id=payment.id,
                    provider=payment.payment_provider,
                    idempotency_key=str(uuid.uuid4()),
                    amount_cents=amount_cents,
                    currency=payment.currency,
                    reason=normalized_reason,
                    status="processing",
                )
                db.session.add(attempt)

            db.session.commit()
            attempt_id = attempt.id

            try:
                result = self.payment_service.refund_payment(
                    payment_id=payment.external_payment_id,
                    amount=attempt.amount_cents,
                    reason=attempt.reason,
                    idempotency_key=attempt.idempotency_key,
                )
            except Exception:
                logger.error("Refund provider outcome is unknown", exc_info=True)
                result = {
                    "success": False,
                    "outcome_known": False,
                    "error": "Refund provider outcome is unknown",
                }

            attempt = RefundAttempt.query.with_for_update().filter_by(id=attempt_id).one()
            payment = Payment.query.with_for_update().filter_by(id=attempt.payment_id).one()
            order = Order.query.with_for_update().filter_by(id=attempt.order_id).one()

            if attempt.status == "succeeded":
                refund = Refund.query.filter_by(external_refund_id=attempt.external_refund_id).one()
                return {"success": True, "refund": refund.to_dict()}

            if result.get("success"):
                external_refund_id = result.get("refund_id")
                if not external_refund_id:
                    raise RuntimeError("provider success lacked refund identity")
                refund = Refund.query.filter_by(external_refund_id=external_refund_id).first()
                if not refund:
                    refund = Refund(
                        order_id=order.id,
                        payment_id=payment.id,
                        refund_amount=Decimal(attempt.amount_cents) / 100,
                        currency=attempt.currency,
                        reason=attempt.reason,
                        external_refund_id=external_refund_id,
                        provider_response=result,
                        processed_at=datetime.now(timezone.utc),
                    )
                    db.session.add(refund)
                    db.session.flush()

                attempt.status = "succeeded"
                attempt.external_refund_id = external_refund_id
                attempt.provider_response = result
                attempt.completed_at = datetime.now(timezone.utc)

                refunded = db.session.query(
                    func.coalesce(func.sum(Refund.refund_amount), 0)
                ).filter_by(payment_id=payment.id).scalar()
                fully_refunded = Decimal(str(refunded)) >= Decimal(str(payment.amount))
                payment.status = (
                    PaymentStatus.REFUNDED if fully_refunded
                    else PaymentStatus.PARTIALLY_REFUNDED
                )
                order.payment_status = payment.status
                if fully_refunded:
                    order.status = OrderStatus.REFUNDED
                db.session.commit()
                return {"success": True, "refund": refund.to_dict()}

            if result.get("outcome_known", True):
                attempt.status = "failed"
                attempt.last_error_code = "provider_rejected"
                attempt.provider_response = {"success": False, "outcome_known": True}
                db.session.commit()
                return {"success": False, "error": result.get("error", "Refund failed"), "code": "REFUND_REJECTED"}

            attempt.status = "unknown"
            attempt.last_error_code = "provider_outcome_unknown"
            attempt.provider_response = {"success": False, "outcome_known": False}
            db.session.commit()
            return {
                "success": False,
                "error": "Refund status is being reconciled; do not submit another refund",
                "code": "REFUND_OUTCOME_UNKNOWN",
            }
        except (SQLAlchemyError, ValueError, TypeError, RuntimeError):
            logger.error("Refund reconciliation failed", exc_info=True)
            db.session.rollback()
            if attempt_id is not None:
                try:
                    attempt = RefundAttempt.query.filter_by(id=attempt_id).first()
                    if attempt and attempt.status != "succeeded":
                        attempt.status = "unknown"
                        attempt.last_error_code = "local_reconciliation_failed"
                        db.session.commit()
                except SQLAlchemyError:
                    db.session.rollback()
            return {
                "success": False,
                "error": "Refund status is being reconciled; do not submit another refund",
                "code": "REFUND_RECONCILIATION_FAILED",
            }
