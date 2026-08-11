"""Durable receipts for payment-provider webhook delivery."""

from sqlalchemy import JSON, func

from server.config import database as db


class SquareWebhookReceipt(db.Model):
    """A replay-safe, durable inbox entry keyed by Square event ID."""

    __tablename__ = "square_webhook_receipts"

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.String(255), nullable=False, unique=True, index=True)
    event_type = db.Column(db.String(120), nullable=False)
    payload_sha256 = db.Column(db.String(64), nullable=False)
    payload = db.Column(JSON, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="received", index=True)
    attempts = db.Column(db.Integer, nullable=False, default=0)
    last_error_code = db.Column(db.String(120), nullable=True)
    received_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    last_attempt_at = db.Column(db.DateTime, nullable=True)
    processed_at = db.Column(db.DateTime, nullable=True)

