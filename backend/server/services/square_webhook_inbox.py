"""Durable registration and replay control for Square webhook events."""

from datetime import datetime, timedelta
import hashlib

from sqlalchemy import and_, or_
from sqlalchemy.exc import IntegrityError

from server.config import database as db
from server.models.webhook import SquareWebhookReceipt


class WebhookEventConflict(ValueError):
    """The provider reused an event ID with different content."""


def payload_digest(raw_payload: bytes) -> str:
    return hashlib.sha256(raw_payload).hexdigest()


def register_event(event_id, event_type, event, raw_payload):
    """Persist the event before processing; concurrent inserts converge safely."""
    digest = payload_digest(raw_payload)
    receipt = SquareWebhookReceipt(
        event_id=event_id,
        event_type=event_type,
        payload_sha256=digest,
        payload=event,
        status="received",
    )
    db.session.add(receipt)
    try:
        db.session.commit()
        return receipt, True
    except IntegrityError:
        db.session.rollback()

    receipt = SquareWebhookReceipt.query.filter_by(event_id=event_id).one()
    if receipt.payload_sha256 != digest:
        raise WebhookEventConflict(event_id)
    return receipt, False


def claim_event(receipt_id, lease_seconds=300):
    """Atomically claim a new/failed event, or reclaim an abandoned lease."""
    now = datetime.utcnow()
    stale_before = now - timedelta(seconds=lease_seconds)
    eligible = or_(
        SquareWebhookReceipt.status.in_(("received", "failed")),
        and_(
            SquareWebhookReceipt.status == "processing",
            SquareWebhookReceipt.last_attempt_at < stale_before,
        ),
    )
    count = (
        SquareWebhookReceipt.query.filter(
            SquareWebhookReceipt.id == receipt_id, eligible
        )
        .update(
            {
                SquareWebhookReceipt.status: "processing",
                SquareWebhookReceipt.attempts: SquareWebhookReceipt.attempts + 1,
                SquareWebhookReceipt.last_attempt_at: now,
                SquareWebhookReceipt.last_error_code: None,
            },
            synchronize_session=False,
        )
    )
    db.session.commit()
    return count == 1


def mark_processed(receipt_id):
    SquareWebhookReceipt.query.filter_by(id=receipt_id).update(
        {
            SquareWebhookReceipt.status: "processed",
            SquareWebhookReceipt.processed_at: datetime.utcnow(),
            SquareWebhookReceipt.last_error_code: None,
        },
        synchronize_session=False,
    )
    db.session.commit()


def mark_failed(receipt_id, error):
    db.session.rollback()
    SquareWebhookReceipt.query.filter_by(id=receipt_id).update(
        {
            SquareWebhookReceipt.status: "failed",
            SquareWebhookReceipt.last_error_code: type(error).__name__[:120],
        },
        synchronize_session=False,
    )
    db.session.commit()

