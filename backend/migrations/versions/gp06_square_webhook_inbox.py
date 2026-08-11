"""Add the durable Square webhook inbox.

Revision ID: gp06_square_webhook_inbox
Revises: gp01_pricing_policy
"""

from alembic import op
import sqlalchemy as sa


revision = "gp06_square_webhook_inbox"
down_revision = "gp01_pricing_policy"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "square_webhook_receipts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("event_id", sa.String(length=255), nullable=False),
        sa.Column("event_type", sa.String(length=120), nullable=False),
        sa.Column("payload_sha256", sa.String(length=64), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("last_error_code", sa.String(length=120), nullable=True),
        sa.Column("received_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("last_attempt_at", sa.DateTime(), nullable=True),
        sa.Column("processed_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_id", name="uq_square_webhook_receipts_event_id"),
    )
    op.create_index(
        "ix_square_webhook_receipts_event_id",
        "square_webhook_receipts",
        ["event_id"],
        unique=True,
    )
    op.create_index(
        "ix_square_webhook_receipts_status",
        "square_webhook_receipts",
        ["status"],
        unique=False,
    )


def downgrade():
    raise RuntimeError("gp06_square_webhook_inbox is forward-only")

