"""Backfill address columns required by auth registration

Revision ID: a7c9d2e4f1b6
Revises: f3a5c1d8e9b0
Create Date: 2026-06-20 03:18:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a7c9d2e4f1b6'
down_revision = 'f3a5c1d8e9b0'
branch_labels = None
depends_on = None


def _has_column(inspector, table_name, column_name):
    return any(column['name'] == column_name for column in inspector.get_columns(table_name))


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if 'addresses' in tables:
        with op.batch_alter_table('addresses', schema=None) as batch_op:
            if not _has_column(inspector, 'addresses', 'is_default'):
                batch_op.add_column(sa.Column('is_default', sa.Boolean(), nullable=False, server_default=sa.false()))
            if not _has_column(inspector, 'addresses', 'created_at'):
                batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()))
            if not _has_column(inspector, 'addresses', 'updated_at'):
                batch_op.add_column(sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()))


def downgrade():
    pass
