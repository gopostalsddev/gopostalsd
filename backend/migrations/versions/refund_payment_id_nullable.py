"""Make refunds.payment_id nullable (admin may refund before Payment row exists)

Revision ID: refund_payment_id_nullable
Revises: widen_price_columns
Branch Labels: None
Depends On: None
"""
from alembic import op
import sqlalchemy as sa

revision = 'refund_payment_id_nullable'
down_revision = 'widen_price_columns'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        'refunds', 'payment_id',
        existing_type=sa.Integer(),
        nullable=True,
    )


def downgrade():
    op.alter_column(
        'refunds', 'payment_id',
        existing_type=sa.Integer(),
        nullable=False,
    )
