"""Merge all migration heads

Revision ID: 009c841ab1e9
Revises: 96823bfbfdaf, add_pricing_models, b9c79d8c68e2, create_vendors_table
Create Date: 2025-09-28 00:42:28.292369

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '009c841ab1e9'
down_revision = ('96823bfbfdaf', 'add_pricing_models', 'b9c79d8c68e2', 'create_vendors_table')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
