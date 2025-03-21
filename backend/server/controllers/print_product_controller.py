from server.controllers import Result
from enum import Enum
from server.config import sinalite
from server.config import database as db
from server.models.print_product import PrintProductCategory


class PrintProductErrors(Enum):
    FAILED_TO_FETCH_PRINT_PRODUCTS = "Failed to fetch products"
    FAILED_TO_FETCH_PRINT_PRODUCT_CATEGORIES = "Failed to fetch print product categories"
    FAILED_TO_FETCH_ENABLED_PRINT_PRODUCT_CATEGORIES = "Failed to fetch enabled print product categories"
    PRINT_PRODUCT_CATEGORY_NOT_FOUND = "Print product category not found"
    

class PrintProductSuccessMessages(Enum):
    UPDATED_PRINT_PRODUCT_CATEGORY_STATUS_SUCCESSFULLY = "Updated print product category status successfully"
    PRINT_PRODUCT_CATEGORY_IN_SYNC = "Print products are in sync"

class PrintProductController:

    @staticmethod
    def get_all_product_categories() -> Result:
        """Retrieve all product categories from the database."""

        result = Result()
        categories = PrintProductCategory.query.all()

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
        categories = PrintProductCategory.query.filter_by(enabled=True).all()

        if categories:
            result.data = [category.to_dict() for category in categories]
        else:
            result.status = False
            result.error = PrintProductErrors.FAILED_TO_FETCH_ENABLED_PRINT_PRODUCT_CATEGORIES.value

        return result

    @staticmethod
    def update_print_product_category_status(category_id: int, enabled: bool):
        """Enable or disable a category."""
        
        result = Result()
        category =  db.session.get(PrintProductCategory, category_id)
        if not category:
            result.status = False
            result.error = PrintProductErrors.PRINT_PRODUCT_CATEGORY_NOT_FOUND.value
            return result
        
        category.enabled = enabled
        db.session.commit()
        result.data = PrintProductSuccessMessages.UPDATED_PRINT_PRODUCT_CATEGORY_STATUS_SUCCESSFULLY.value
        return result

    @staticmethod
    def sync_print_product_categories() -> Result:
        """Sync categories from Sinalite API (manual trigger)."""
        result =  Result
        sinalite_categories = sinalite.get_product_categories()
        existing_categories = [category.name for category in [category_instance.to_dict() for category_instance in PrintProductCategory.query.all()]]
        new_categories = [PrintProductCategory(name=name) for name in sinalite_categories if name not in existing_categories]

        if new_categories:
            db.session.bulk_save_objects(new_categories)
            db.session.commit()

        result.data = PrintProductSuccessMessages.PRINT_PRODUCT_CATEGORY_IN_SYNC.value
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
        pass

