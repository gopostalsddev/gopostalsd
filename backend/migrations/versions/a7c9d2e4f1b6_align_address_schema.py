"""Align address schema with current models

Revision ID: a7c9d2e4f1b6
Revises: f3a5c1d8e9b0
Create Date: 2026-06-21 22:46:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'a7c9d2e4f1b6'
down_revision = 'f3a5c1d8e9b0'
branch_labels = None
depends_on = None


def _has_column(inspector, table_name, column_name):
    return any(column['name'] == column_name for column in inspector.get_columns(table_name))


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if 'addresses' not in inspector.get_table_names():
        return

    address_columns = {column['name'] for column in inspector.get_columns('addresses')}

    if 'is_default' not in address_columns:
        op.add_column(
            'addresses',
            sa.Column('is_default', sa.Boolean(), nullable=False, server_default=sa.false()),
        )
    if 'created_at' not in address_columns:
        op.add_column(
            'addresses',
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )
    if 'updated_at' not in address_columns:
        op.add_column(
            'addresses',
            sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )


def downgrade():
    pass
