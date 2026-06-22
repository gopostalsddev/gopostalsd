"""Make product option uniqueness product-scoped

Revision ID: prod_opt_unique_per_product
Revises: order_mgmt_tables
Create Date: 2026-06-22 01:05:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'prod_opt_unique_per_product'
down_revision = 'order_mgmt_tables'
branch_labels = None
depends_on = None


def _drop_unique_if_exists(table_name: str, constraint_name: str) -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing = {c.get('name') for c in inspector.get_unique_constraints(table_name)}
    if constraint_name in existing:
        op.drop_constraint(constraint_name, table_name, type_='unique')


def upgrade():
    # Old schema used global uniqueness on sinalite_option_id, which is invalid
    # when the same option id appears under different products.
    _drop_unique_if_exists('product_options', 'product_options_sinalite_option_id_key')
    _drop_unique_if_exists('product_options', 'uq_product_options_product_option')

    op.create_unique_constraint(
        'uq_product_options_product_option',
        'product_options',
        ['product_id', 'sinalite_option_id'],
    )


def downgrade():
    _drop_unique_if_exists('product_options', 'uq_product_options_product_option')

    op.create_unique_constraint(
        'product_options_sinalite_option_id_key',
        'product_options',
        ['sinalite_option_id'],
    )
