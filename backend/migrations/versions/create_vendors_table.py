"""Create vendors table

Revision ID: create_vendors_table
Revises: populate_classification_status
Create Date: 2025-08-19 01:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'create_vendors_table'
down_revision = 'create_unclassified_product_type'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    dialect_name = connection.engine.dialect.name

    # Create vendors table
    op.create_table('vendors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Insert seed data
    op.execute("INSERT INTO vendors (id, name) VALUES (0, 'Native')")
    op.execute("INSERT INTO vendors (id, name) VALUES (1, 'Sinalite')")
    
    # Add vendor_id and vendor_product_id to print_products table
    op.add_column('print_products', sa.Column('vendor_id', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('print_products', sa.Column('vendor_product_id', sa.String(length=255), nullable=True))
    
    # Add foreign key constraint where supported.
    if dialect_name != 'sqlite':
        op.create_foreign_key('fk_print_products_vendor_id', 'print_products', 'vendors', ['vendor_id'], ['id'])
    
    # Create index on vendor_product_id for performance
    op.create_index('ix_print_products_vendor_product_id', 'print_products', ['vendor_product_id'])


def downgrade():
    connection = op.get_bind()
    dialect_name = connection.engine.dialect.name

    # Remove foreign key constraint
    if dialect_name != 'sqlite':
        op.drop_constraint('fk_print_products_vendor_id', 'print_products', type_='foreignkey')
    
    # Remove index
    op.drop_index('ix_print_products_vendor_product_id', table_name='print_products')
    
    # Remove columns
    op.drop_column('print_products', 'vendor_product_id')
    op.drop_column('print_products', 'vendor_id')
    
    # Drop vendors table
    op.drop_table('vendors') 