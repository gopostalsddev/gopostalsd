"""Add durable refund attempts and provider refund uniqueness.

Revision ID: gp08_refund_attempts
Revises: gp07_payment_attempts
"""

from alembic import op
import sqlalchemy as sa


revision = "gp08_refund_attempts"
down_revision = "gp07_payment_attempts"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "refund_attempts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("payment_id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("idempotency_key", sa.String(length=64), nullable=False),
        sa.Column("amount_cents", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("reason", sa.String(length=500), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("external_refund_id", sa.String(length=255), nullable=True),
        sa.Column("provider_response", sa.JSON(), nullable=True),
        sa.Column("last_error_code", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"]),
        sa.ForeignKeyConstraint(["payment_id"], ["payments.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("idempotency_key", name="uq_refund_attempts_idempotency_key"),
        sa.UniqueConstraint("external_refund_id", name="uq_refund_attempts_external_refund_id"),
    )
    op.create_index("ix_refund_attempts_order_id", "refund_attempts", ["order_id"])
    op.create_index("ix_refund_attempts_payment_id", "refund_attempts", ["payment_id"])
    op.create_index("ix_refund_attempts_status", "refund_attempts", ["status"])
    op.create_unique_constraint(
        "uq_refunds_external_refund_id", "refunds", ["external_refund_id"]
    )


def downgrade():
    raise RuntimeError("gp08_refund_attempts is forward-only")
