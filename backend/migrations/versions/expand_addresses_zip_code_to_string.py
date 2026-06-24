"""Expand addresses.zip_code to string

Revision ID: zip_code_to_string
Revises: fix_roles_varchar_length
Create Date: 2026-06-21 20:33:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = 'zip_code_to_string'
down_revision = 'fix_roles_varchar_length'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if 'addresses' not in inspector.get_table_names():
        return

    zip_col = next(
        (column for column in inspector.get_columns('addresses') if column['name'] == 'zip_code'),
        None,
    )
    if not zip_col or 'INT' not in str(zip_col['type']).upper():
        return

    if bind.dialect.name == 'postgresql':
        op.alter_column(
            'addresses',
            'zip_code',
            existing_type=zip_col['type'],
            type_=sa.String(length=20),
            existing_nullable=zip_col.get('nullable', False),
            postgresql_using='zip_code::text',
        )
        return

    with op.batch_alter_table('addresses', schema=None) as batch_op:
        batch_op.alter_column(
            'zip_code',
            existing_type=zip_col['type'],
            type_=sa.String(length=20),
            existing_nullable=zip_col.get('nullable', False),
        )


def downgrade():
    pass
