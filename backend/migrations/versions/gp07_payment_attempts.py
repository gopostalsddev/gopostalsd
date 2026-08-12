"""Add durable payment attempts and provider payment uniqueness.

Revision ID: gp07_payment_attempts
Revises: gp06_square_webhook_inbox
"""

from alembic import op
import sqlalchemy as sa


revision = "gp07_payment_attempts"
down_revision = "gp06_square_webhook_inbox"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "payment_attempts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("idempotency_key", sa.String(length=64), nullable=False),
        sa.Column("provider_reference", sa.String(length=64), nullable=False),
        sa.Column("source_fingerprint", sa.String(length=64), nullable=False),
        sa.Column("amount_cents", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("external_payment_id", sa.String(length=255), nullable=True),
        sa.Column("provider_response", sa.JSON(), nullable=True),
        sa.Column("last_error_code", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("idempotency_key", name="uq_payment_attempts_idempotency_key"),
        sa.UniqueConstraint("provider_reference", name="uq_payment_attempts_provider_reference"),
        sa.UniqueConstraint("external_payment_id", name="uq_payment_attempts_external_payment_id"),
    )
    op.create_index("ix_payment_attempts_order_id", "payment_attempts", ["order_id"])
    op.create_index("ix_payment_attempts_status", "payment_attempts", ["status"])
    op.create_unique_constraint(
        "uq_payments_provider_external_id",
        "payments",
        ["payment_provider", "external_payment_id"],
    )


def downgrade():
    raise RuntimeError("gp07_payment_attempts is forward-only")
