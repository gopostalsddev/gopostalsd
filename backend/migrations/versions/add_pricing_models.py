"""Add pricing and cart models

Revision ID: add_pricing_models
Revises: create_unclassified_product_type
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_pricing_models'
down_revision = 'create_unclassified_product_type'
branch_labels = None
depends_on = None


def upgrade():
    # Create product_options table
    op.create_table('product_options',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sinalite_option_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('group', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('sinalite_option_id')
    )
    op.create_index(op.f('ix_product_options_product_id'), 'product_options', ['product_id'], unique=False)

    # Create product_pricing table
    op.create_table('product_pricing',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('store_code', sa.Integer(), nullable=False),
        sa.Column('option_key', sa.String(length=500), nullable=False),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('package_info', sa.JSON(), nullable=True),
        sa.Column('product_options', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('product_id', 'store_code', 'option_key', name='unique_pricing')
    )

    # Create carts table
    op.create_table('carts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(length=255), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('store_code', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_id')
    )

    # Create cart_items table
    op.create_table('cart_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cart_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('product_name', sa.String(length=255), nullable=False),
        sa.Column('product_sku', sa.String(length=255), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('selected_options', sa.JSON(), nullable=False),
        sa.Column('option_key', sa.String(length=500), nullable=False),
        sa.Column('unit_price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('total_price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('package_info', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['cart_id'], ['carts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create shipping_options table
    op.create_table('shipping_options',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cart_id', sa.Integer(), nullable=False),
        sa.Column('carrier_name', sa.String(length=100), nullable=False),
        sa.Column('method_name', sa.String(length=100), nullable=False),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('shipping_days', sa.Integer(), nullable=False),
        sa.Column('destination_state', sa.String(length=10), nullable=True),
        sa.Column('destination_zip', sa.String(length=20), nullable=True),
        sa.Column('destination_country', sa.String(length=10), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['cart_id'], ['carts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create product_variants table
    op.create_table('product_variants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('variant_key', sa.String(length=500), nullable=False),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('product_id', 'variant_key', name='unique_variant')
    )


def downgrade():
    # Drop tables in reverse order
    op.drop_table('product_variants')
    op.drop_table('shipping_options')
    op.drop_table('cart_items')
    op.drop_table('carts')
    op.drop_table('product_pricing')
    op.drop_table('product_options')
