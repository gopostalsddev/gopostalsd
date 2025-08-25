"""Create unclassified product type and update schema

Revision ID: create_unclassified_product_type
Revises: populate_classification_status
Create Date: 2025-01-27 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = 'create_unclassified_product_type'
down_revision = 'populate_classification_status'
branch_labels = None
depends_on = None


def upgrade():
    # Get database connection
    connection = op.get_bind()
    
    # 1. Make category_id nullable in print_product_types for the wildcard type
    op.alter_column('print_product_types', 'category_id', nullable=True)
    
    # 2. Insert the unclassified product type with ID 0
    connection.execute(text("""
        INSERT INTO print_product_types (id, name, description, category_id, created_at, updated_at)
        VALUES (0, 'Unclassified', 'Default type for products not yet classified', NULL, NOW(), NOW())
        ON CONFLICT (id) DO NOTHING;
    """))
    
    # 3. Update existing products with NULL type_id to use ID 0
    connection.execute(text("""
        UPDATE print_products 
        SET type_id = 0 
        WHERE type_id IS NULL;
    """))
    
    # 4. Make type_id NOT NULL with default 0 in print_products
    op.alter_column('print_products', 'type_id', nullable=False, server_default='0')
    
    # 5. Update classification status for all categories to reflect the new structure
    connection.execute(text("""
        UPDATE print_product_categories 
        SET product_classification_status = (
            SELECT json_build_object(
                'all_classified', 
                CASE 
                    WHEN COUNT(p.id) = 0 THEN true
                    ELSE COUNT(p.id) = COUNT(CASE WHEN p.type_id > 0 THEN 1 END)
                END,
                'total_products', COUNT(p.id),
                'classified_products', COUNT(CASE WHEN p.type_id > 0 THEN 1 END),
                'unclassified_products', COUNT(CASE WHEN p.type_id = 0 THEN 1 END)
            )
            FROM print_products p 
            WHERE p.category_id = print_product_categories.id
        )
        WHERE EXISTS (SELECT 1 FROM print_products p WHERE p.category_id = print_product_categories.id)
    """))
    
    # For categories with no products, set default status
    connection.execute(text("""
        UPDATE print_product_categories 
        SET product_classification_status = '{"all_classified": true, "total_products": 0, "classified_products": 0, "unclassified_products": 0}'::json
        WHERE NOT EXISTS (SELECT 1 FROM print_products p WHERE p.category_id = print_product_categories.id)
    """))


def downgrade():
    # Get database connection
    connection = op.get_bind()
    
    # 1. Revert type_id to nullable in print_products
    op.alter_column('print_products', 'type_id', nullable=True, server_default=None)
    
    # 2. Update products with type_id = 0 back to NULL
    connection.execute(text("""
        UPDATE print_products 
        SET type_id = NULL 
        WHERE type_id = 0;
    """))
    
    # 3. Delete the unclassified product type
    connection.execute(text("DELETE FROM print_product_types WHERE id = 0;"))
    
    # 4. Make category_id NOT NULL again in print_product_types
    op.alter_column('print_product_types', 'category_id', nullable=False)
    
    # 5. Revert classification status to use NULL checks
    connection.execute(text("""
        UPDATE print_product_categories 
        SET product_classification_status = (
            SELECT json_build_object(
                'all_classified', 
                CASE 
                    WHEN COUNT(p.id) = 0 THEN true
                    ELSE COUNT(p.id) = COUNT(CASE WHEN p.type_id IS NOT NULL THEN 1 END)
                END,
                'total_products', COUNT(p.id),
                'classified_products', COUNT(CASE WHEN p.type_id IS NOT NULL THEN 1 END),
                'unclassified_products', COUNT(CASE WHEN p.type_id IS NULL THEN 1 END)
            )
            FROM print_products p 
            WHERE p.category_id = print_product_categories.id
        )
        WHERE EXISTS (SELECT 1 FROM print_products p WHERE p.category_id = print_product_categories.id)
    """)) 