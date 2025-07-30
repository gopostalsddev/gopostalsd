from server.controllers import Result
from enum import Enum
from server.config import sinalite
from server.config import database as db
from server.models.print_product import PrintProductCategory
from markupsafe import escape
import logging
from werkzeug.datastructures import FileStorage
from flask import current_app

logger = logging.getLogger(__name__)

class PrintProductErrors(Enum):
    FAILED_TO_FETCH_PRINT_PRODUCTS = "Failed to fetch products"
    FAILED_TO_FETCH_PRINT_PRODUCT_CATEGORIES = "Failed to fetch print product categories"
    FAILED_TO_FETCH_ENABLED_PRINT_PRODUCT_CATEGORIES = "Failed to fetch enabled print product categories"
    PRINT_PRODUCT_CATEGORY_NOT_FOUND = "Print product category not found"
    FAILED_TO_UPDATE_PRODUCT_CATEGORY = "Failed to update product categories"
    PRINT_PRODUCT_DESCRIPTION_TOO_LONG = "Description is too long (max 1000 characters)."
    INVALID_IMAGE_FILE = "Invalid imege"
    INVALID_IMAGE_URL = "Invalid image URL. Must start with http:// or https://"
    
class PrintProductSuccessMessages(Enum):
    UPDATED_PRINT_PRODUCT_CATEGORY_STATUS_SUCCESSFULLY = "Updated print product category status successfully"
    PRINT_PRODUCT_CATEGORY_IN_SYNC = "Print products are in sync"
    PRODUCT_CATEGORY_UPDATED_SUCCESSFULLY = "Product category updated successfully"

class PrintProductController:

    @staticmethod
    def get_all_product_categories() -> Result:
        """Retrieve all product categories from the database."""

        result = Result()

        table_is_empty = (PrintProductCategory.query.first() is None) # TODO: Add test case
        if(table_is_empty):
            result.data = []
            return result

        # Always fetch categories sorted by name
        categories = PrintProductCategory.query.order_by(PrintProductCategory.name.asc()).all()

        if categories:
            result.data = [category.to_dict() for category in categories]
        else:
            result.status = False
            result.error = PrintProductErrors.FAILED_TO_FETCH_PRINT_PRODUCT_CATEGORIES.value
        
        return result

    @staticmethod
    def get_enabled_product_categories() -> Result:
        """Retrieve only enabled categories."""
        
        result = Result()

        table_is_empty = (PrintProductCategory.query.first() is None) # TODO: Add test case
        if(table_is_empty):
            result.data = []
            return result

        logger.info("Fetching enabled categories ... ")
        categories = PrintProductCategory.query.filter_by(enabled=True).all()
       
        num_categories = len(categories)
        if num_categories == 1:
            logger.info(f"Found {num_categories} enabled category ... ")
            result.data = [categories[0].to_dict()]
        else:
            logger.info(f"Found {num_categories} enabled categories ... ")
            result.data = [category.to_dict() for category in categories]
        
        return result

    @staticmethod
    def update_print_product_category_status(category_id: int, enabled: bool):
        """Enable or disable a category."""
        result = Result()

        try:
            table_is_empty = (PrintProductCategory.query.first() is None)  # TODO: Add test case
            if table_is_empty:
                result.data = []
                return result

            # Fetch the category by ID
            category = db.session.get(PrintProductCategory, category_id)
            if not category:
                logger.warning(f"Category with ID {category_id} not found.")
                result.status = False
                result.error = PrintProductErrors.PRINT_PRODUCT_CATEGORY_NOT_FOUND.value
                return result

            # Update category status
            category.enabled = enabled
            db.session.commit()  

            result.data = {"message": PrintProductSuccessMessages.UPDATED_PRINT_PRODUCT_CATEGORY_STATUS_SUCCESSFULLY.value}
        
        except Exception as e:
            logger.error(f"Failed to update category status: {e}")
            db.session.rollback()  # Rollback in case of failure
            result.status = False
            result.error = "An error occurred while updating the category."
        

        return result

    @staticmethod
    def sync_print_product_categories() -> Result:
        """Sync categories from Sinalite API (manual trigger)."""
        result = Result()

        logger.info("Requesting all product categories from Sinalite ...")
        try:
            sinalite_categories = sinalite.get_product_categories()
            if not sinalite_categories:
                raise ValueError("No categories returned from Sinalite API")
        except Exception as e:
            logger.error(f"Failed to fetch categories from Sinalite API: {e}")
            result.data = {"message": "Failed to sync product categories"}
            return result

        logger.info("Fetching all product categories currently known ...")
        try:
            existing_categories = {
                category.name for category in PrintProductCategory.query.with_entities(PrintProductCategory.name).all()
            }
        except Exception as e:
            logger.error(f"Failed to fetch existing product categories: {e}")
            result.data = {"message": "Failed to sync product categories"}
            return result

        new_categories = [
            PrintProductCategory(name=name) for name in sinalite_categories if name not in existing_categories
        ]

        logger.info(f"Found {len(new_categories)} new {'category' if len(new_categories) == 1 else 'categories'} ...")

        if new_categories:
            logger.info("Syncing product categories ...")
            try:
                db.session.bulk_save_objects(new_categories) 
                db.session.commit() 
                logger.info("Synced product categories successfully ...")
            except Exception as e:
                logger.error(f"Failed to sync new product categories: {e}")
                db.session.rollback()  # ✅ Rollback in case of failure
                result.data = {"message": "Failed to sync product categories"}
                return result

        result.data = {"message": PrintProductSuccessMessages.PRINT_PRODUCT_CATEGORY_IN_SYNC.value}
        return result

    @staticmethod
    def get_all_products() -> Result:
        """Fetch print products from Sinalite"""

        result = Result()
        products = sinalite.get_products()

        if products:
            result.data = products
        else:
            result.status = False
            result.error = PrintProductErrors.FAILED_TO_FETCH_PRINT_PRODUCTS.value
        
        return result
    
    @staticmethod
    def get_products_by_category(category: str) -> Result:
        """Fetch print products from Sinalite API by category, esuring category is enabled in the database"""
        result = Result()

        table_is_empty = (PrintProductCategory.query.first() is None) # TODO: Add test case
        if(table_is_empty):
            result.data = []
            return result

        # Validate category exists and is enabled in the database
        local_category = PrintProductCategory.query.filter_by(name=category, enabled=True).first()
        if not local_category:
            result.status = False
            result.error = PrintProductErrors.PRINT_PRODUCT_CATEGORY_NOT_FOUND.value
            return result
        
        # Fetch all products from sinalite
        all_products = sinalite.get_products()

        # Filter products by category
        filtered_products = [product for product in all_products if product['category'] == category]

        # Always return a list even if empty
        result.data = filtered_products

        return result

    @staticmethod
    def update_print_product_category(category_id: int, description: str = None, image=None):
        """Update the description or image of a product category securely"""
        result = Result()

        try:
            category = db.session.get(PrintProductCategory, category_id)

            if not category:
                result.status = False
                result.error = PrintProductErrors.PRINT_PRODUCT_CATEGORY_NOT_FOUND.value
                return result

            # Sanitize and validate description
            if description:
                description = escape(description.strip())
                if len(description) > 1000:
                    result.status = False
                    result.error = PrintProductErrors.PRINT_PRODUCT_DESCRIPTION_TOO_LONG.value
                    return result
                category.description = description

            # Handle image upload
            if image:
                if isinstance(image, FileStorage):
                    # Ensure file is not empty
                    if image.filename == "":
                        result.status = False
                        result.error = PrintProductErrors.EMPTY_IMAGE_FILE.value
                        return result

                    content_type = image.content_type
                    filename = image.filename
                    file_data = image.read()

                    # Upload file using current filestorage
                    filestorage = current_app.extensions["filestorage"]
                    image_url = filestorage.upload_file(file_data, filename, content_type)
                    print(f"Image URL {image_url}")

                    # Save URL in DB
                    category.image = image_url
                else:
                    result.status = False
                    result.error = PrintProductErrors.INVALID_IMAGE_FILE.value
                    return result

            db.session.commit()
            result.data = {"message": PrintProductSuccessMessages.PRODUCT_CATEGORY_UPDATED_SUCCESSFULLY.value}

        except Exception as e:
            db.session.rollback()
            result.status = False
            result.error = f"{PrintProductErrors.FAILED_TO_UPDATE_PRODUCT_CATEGORY.value}: {str(e)}"

        return result