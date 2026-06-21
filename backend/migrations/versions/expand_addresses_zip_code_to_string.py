"""Expand addresses.zip_code to string

Revision ID: zip_code_to_string
Revises: fix_roles_varchar_length
Create Date: 2026-06-21 20:33:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'zip_code_to_string'
down_revision = 'fix_roles_varchar_length'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()

    if bind.dialect.name == 'postgresql':
        op.alter_column(
            'addresses',
            'zip_code',
            existing_type=sa.Integer(),
            type_=sa.String(length=20),
            existing_nullable=False,
            postgresql_using='zip_code::text'
        )
        return

    with op.batch_alter_table('addresses', schema=None) as batch_op:
        batch_op.alter_column(
            'zip_code',
            existing_type=sa.Integer(),
            type_=sa.String(length=20),
            existing_nullable=False
        )


def downgrade():
    bind = op.get_bind()

    if bind.dialect.name == 'postgresql':
        op.alter_column(
            'addresses',
            'zip_code',
            existing_type=sa.String(length=20),
            type_=sa.Integer(),
            existing_nullable=False,
            postgresql_using='NULLIF(regexp_replace(zip_code, ''[^0-9]'', '''', ''g''), '''')::integer'
        )
        return

    with op.batch_alter_table('addresses', schema=None) as batch_op:
        batch_op.alter_column(
            'zip_code',
            existing_type=sa.String(length=20),
            type_=sa.Integer(),
            existing_nullable=False
        )