"""Widen price columns to NUMERIC(15,4) to prevent overflow on large Sinalite values

Revision ID: widen_price_columns
Revises: prod_opt_unique_per_product
Branch Labels: None
Depends On: None
"""
from alembic import op
import sqlalchemy as sa

revision = 'widen_price_columns'
down_revision = 'prod_opt_unique_per_product'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('product_variants', 'price',
                    existing_type=sa.Numeric(10, 2),
                    type_=sa.Numeric(15, 4),
                    existing_nullable=False)
    op.alter_column('product_pricing', 'price',
                    existing_type=sa.Numeric(10, 2),
                    type_=sa.Numeric(15, 4),
                    existing_nullable=False)


def downgrade():
    op.alter_column('product_pricing', 'price',
                    existing_type=sa.Numeric(15, 4),
                    type_=sa.Numeric(10, 2),
                    existing_nullable=False)
    op.alter_column('product_variants', 'price',
                    existing_type=sa.Numeric(15, 4),
                    type_=sa.Numeric(10, 2),
                    existing_nullable=False)
