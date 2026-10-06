"""Add order_artwork table for customer artwork uploads.

Revision ID: gp09_order_artwork
Revises: gp08_refund_attempts
"""

from alembic import op
import sqlalchemy as sa


revision = "gp09_order_artwork"
down_revision = "gp08_refund_attempts"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "order_artwork",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("mimetype", sa.String(length=100), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("file_data", sa.LargeBinary(), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_order_artwork_order_id", "order_artwork", ["order_id"])


def downgrade():
    raise RuntimeError("gp09_order_artwork is forward-only")
