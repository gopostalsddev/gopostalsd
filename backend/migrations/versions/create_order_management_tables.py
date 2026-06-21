"""Create order management tables

Revision ID: order_mgmt_tables
Revises: zip_code_to_string
Create Date: 2026-06-21 23:25:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'order_mgmt_tables'
down_revision = 'zip_code_to_string'
branch_labels = None
depends_on = None


def upgrade():
    order_status_enum = sa.Enum(
        'PENDING',
        'PROCESSING',
        'SHIPPED',
        'DELIVERED',
        'CANCELLED',
        'REFUNDED',
        name='orderstatus',
        create_type=False,
    )
    payment_status_enum = sa.Enum(
        'PENDING',
        'PROCESSING',
        'COMPLETED',
        'FAILED',
        'REFUNDED',
        'PARTIALLY_REFUNDED',
        name='paymentstatus',
        create_type=False,
    )

    bind = op.get_bind()
    order_status_enum.create(bind, checkfirst=True)
    payment_status_enum.create(bind, checkfirst=True)

    op.create_table(
        'orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_number', sa.String(length=50), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('session_id', sa.String(length=255), nullable=True),
        sa.Column('customer_email', sa.String(length=120), nullable=False),
        sa.Column('customer_first_name', sa.String(length=60), nullable=False),
        sa.Column('customer_last_name', sa.String(length=60), nullable=False),
        sa.Column('customer_phone', sa.String(length=20), nullable=True),
        sa.Column('status', order_status_enum, nullable=False),
        sa.Column('subtotal', sa.Numeric(10, 2), nullable=False),
        sa.Column('shipping_cost', sa.Numeric(10, 2), nullable=False),
        sa.Column('tax_amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('total_amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('shipping_address', sa.JSON(), nullable=False),
        sa.Column('billing_address', sa.JSON(), nullable=True),
        sa.Column('payment_status', payment_status_enum, nullable=False),
        sa.Column('payment_provider', sa.String(length=50), nullable=True),
        sa.Column('payment_id', sa.String(length=255), nullable=True),
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.Column('tracking_number', sa.String(length=100), nullable=True),
        sa.Column('carrier_name', sa.String(length=50), nullable=True),
        sa.Column('estimated_delivery', sa.DateTime(), nullable=True),
        sa.Column('shipped_at', sa.DateTime(), nullable=True),
        sa.Column('delivered_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order_number'),
    )

    op.create_table(
        'order_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('product_name', sa.String(length=255), nullable=False),
        sa.Column('product_sku', sa.String(length=255), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('selected_options', sa.JSON(), nullable=False),
        sa.Column('option_key', sa.String(length=500), nullable=False),
        sa.Column('unit_price', sa.Numeric(10, 2), nullable=False),
        sa.Column('total_price', sa.Numeric(10, 2), nullable=False),
        sa.Column('package_info', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('payment_provider', sa.String(length=50), nullable=False),
        sa.Column('external_payment_id', sa.String(length=255), nullable=False),
        sa.Column('amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('status', payment_status_enum, nullable=False),
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.Column('card_last_four', sa.String(length=4), nullable=True),
        sa.Column('card_brand', sa.String(length=20), nullable=True),
        sa.Column('provider_response', sa.JSON(), nullable=True),
        sa.Column('failure_reason', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'refunds',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('payment_id', sa.Integer(), nullable=False),
        sa.Column('refund_amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('reason', sa.String(length=500), nullable=True),
        sa.Column('external_refund_id', sa.String(length=255), nullable=True),
        sa.Column('provider_response', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id']),
        sa.ForeignKeyConstraint(['payment_id'], ['payments.id']),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade():
    op.drop_table('refunds')
    op.drop_table('payments')
    op.drop_table('order_items')
    op.drop_table('orders')

    bind = op.get_bind()
    sa.Enum(name='paymentstatus').drop(bind, checkfirst=True)
    sa.Enum(name='orderstatus').drop(bind, checkfirst=True)
