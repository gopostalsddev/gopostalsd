"""Fix roles.name varchar length for RegisteredCustomer

Revision ID: fix_roles_varchar_length
Revises: a7c9d2e4f1b6
Create Date: 2026-06-21 20:21:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fix_roles_varchar_length'
down_revision = 'a7c9d2e4f1b6'
branch_labels = None
depends_on = None


def upgrade():
    # Simple fix: expand roles.name column from VARCHAR(16) to VARCHAR(50)
    # to accommodate role names like 'RegisteredCustomer' (18 chars)
    with op.batch_alter_table('roles', schema=None) as batch_op:
        batch_op.alter_column('name',
               existing_type=sa.VARCHAR(length=16),
               type_=sa.VARCHAR(length=50),
               existing_nullable=False)


def downgrade():
    with op.batch_alter_table('roles', schema=None) as batch_op:
        batch_op.alter_column('name',
               existing_type=sa.VARCHAR(length=50),
               type_=sa.VARCHAR(length=16),
               existing_nullable=False)
