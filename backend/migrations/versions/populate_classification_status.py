"""Populate classification status for existing categories

Revision ID: populate_classification_status
Revises: add_classification_status_field
Create Date: 2025-01-27 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = 'populate_classification_status'
down_revision = 'add_classification_status_field'
branch_labels = None
depends_on = None


def upgrade():
    # Get database connection
    connection = op.get_bind()

    # Support both PostgreSQL and SQLite syntax for local development.
    dialect_name = connection.engine.dialect.name
    
    if dialect_name == 'sqlite':
        # SQLite JSON constructor and booleans differ from PostgreSQL.
        update_query = text("""
            UPDATE print_product_categories
            SET product_classification_status = (
                SELECT json_object(
                    'all_classified',
                    CASE
                        WHEN COUNT(p.id) = 0 THEN 1
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
        """)

        update_empty_query = text("""
            UPDATE print_product_categories
            SET product_classification_status = '{"all_classified": true, "total_products": 0, "classified_products": 0, "unclassified_products": 0}'
            WHERE NOT EXISTS (SELECT 1 FROM print_products p WHERE p.category_id = print_product_categories.id)
        """)
    else:
        # PostgreSQL path used in deployed environments.
        update_query = text("""
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
        """)

        # For categories with no products, set default status
        update_empty_query = text("""
            UPDATE print_product_categories 
            SET product_classification_status = '{"all_classified": true, "total_products": 0, "classified_products": 0, "unclassified_products": 0}'::json
            WHERE NOT EXISTS (SELECT 1 FROM print_products p WHERE p.category_id = print_product_categories.id)
        """)
    
    connection.execute(update_query)
    connection.execute(update_empty_query)


def downgrade():
    # This migration only populates data, so downgrade does nothing
    # The field will still exist but with default values
    pass 