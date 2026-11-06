"""Add sinalite_order_id and shipping_method to orders.

Revision ID: gp10_sinalite_fulfillment
Revises: gp09_order_artwork
"""

from alembic import op
import sqlalchemy as sa


revision = "gp10_sinalite_fulfillment"
down_revision = "gp09_order_artwork"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("orders", sa.Column("sinalite_order_id", sa.Integer(), nullable=True))
    op.add_column("orders", sa.Column("shipping_method", sa.String(100), nullable=True))


def downgrade():
    op.drop_column("orders", "sinalite_order_id")
    op.drop_column("orders", "shipping_method")
