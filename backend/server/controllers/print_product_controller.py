from server.controllers import Result
from enum import Enum
from server.config import sinalite
from server.config import database as db
from server.models.print_product import PrintProductCategory, PrintProductType, PrintProduct, Vendor
from markupsafe import escape
import logging
import os
import uuid
from datetime import datetime
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from flask import current_app

logger = logging.getLogger(__name__)

class PrintProductErrors(Enum):
    FAILED_TO_FETCH_PRINT_PRODUCTS = "Failed to fetch products"
    FAILED_TO_FETCH_PRINT_PRODUCT_CATEGORIES = "Failed to fetch print product categories"
    FAILED_TO_FETCH_ENABLED_PRINT_PRODUCT_CATEGORIES = "Failed to fetch enabled print product categories"
    PRINT_PRODUCT_CATEGORY_NOT_FOUND = "Print product category not found"
    FAILED_TO_UPDATE_PRODUCT_CATEGORY = "Failed to update product categories"
    PRINT_PRODUCT_DESCRIPTION_TOO_LONG = "Description is too long (max 1000 characters)."
    INVALID_IMAGE_FILE = "Invalid image"
    EMPTY_IMAGE_FILENAME = "Empty image filename"
    INVALID_IMAGE_URL = "Invalid image URL. Must start with http:// or https://"
    
    # Product Type specific errors
    PRINT_PRODUCT_TYPE_NOT_FOUND = "Print product type not found"
    FAILED_TO_CREATE_PRODUCT_TYPE = "Failed to create product type"
    FAILED_TO_UPDATE_PRODUCT_TYPE = "Failed to update product type"
    FAILED_TO_DELETE_PRODUCT_TYPE = "Failed to delete product type"
    PRODUCT_TYPE_NAME_REQUIRED = "Product type name is required"
    PRODUCT_TYPE_CATEGORY_ID_REQUIRED = "Product type category ID is required"
    PRODUCT_TYPE_DESCRIPTION_REQUIRED = "Product type description is required"
    PRODUCT_TYPE_CATEGORY_NOT_FOUND = "Product type category not found"
    PRODUCT_TYPE_NAME_ALREADY_EXISTS = "Product type name already exists in this category"
    PRODUCT_TYPE_IN_USE = "Cannot delete product type: It is being used by existing products"
    PRODUCT_TYPE_NAME_TOO_LONG = "Product type name is too long (max 255 characters)"
    PRODUCT_TYPE_NAME_TOO_SHORT = "Product type name is too short (min 2 characters)"
    FAILED_TO_FETCH_PRINT_PRODUCT_TYPES = "Failed to fetch print product types"
    
class PrintProductSuccessMessages(Enum):
    UPDATED_PRINT_PRODUCT_CATEGORY_STATUS_SUCCESSFULLY = "Updated print product category status successfully"
    PRINT_PRODUCT_CATEGORY_IN_SYNC = "Print products are in sync"
    PRODUCT_CATEGORY_UPDATED_SUCCESSFULLY = "Product category updated successfully"
    
    # Product Type specific success messages
    PRODUCT_TYPE_CREATED_SUCCESSFULLY = "Product type created successfully"
    PRODUCT_TYPE_UPDATED_SUCCESSFULLY = "Product type updated successfully"
    PRODUCT_TYPE_DELETED_SUCCESSFULLY = "Product type deleted successfully"
    PRINT_PRODUCTS_SYNCED_SUCCESSFULLY = "Print products synced successfully"

class PrintProductController:

    @staticmethod
    def create_manual_product(data: dict) -> Result:
        """Create a manual product entry for non-Sinalite or manually managed vendors."""
        result = Result()

        try:
            name = (data.get('name') or '').strip()
            sku = (data.get('sku') or '').strip()
            description = (data.get('description') or '').strip() or None
            image = (data.get('image') or '').strip() or None
            vendor_product_id = (data.get('vendor_product_id') or '').strip() or None
            category_id = data.get('category_id')
            type_id = data.get('type_id') or 0
            vendor_id = data.get('vendor_id')

            if not name:
                result.status = False
                result.error = 'Product name is required'
                return result
            if not sku:
                result.status = False
                result.error = 'SKU is required'
                return result
            if not category_id:
                result.status = False
                result.error = 'category_id is required'
                return result
            if not vendor_id:
                result.status = False
                result.error = 'vendor_id is required'
                return result

            category = db.session.get(PrintProductCategory, int(category_id))
            vendor = db.session.get(Vendor, int(vendor_id))
            product_type = db.session.get(PrintProductType, int(type_id)) if int(type_id) > 0 else None

            if not category:
                result.status = False
                result.error = 'Category not found'
                return result
            if not vendor:
                result.status = False
                result.error = 'Vendor not found'
                return result
            if product_type and product_type.category_id != category.id:
                result.status = False
                result.error = 'Selected product type does not belong to this category'
                return result
            if PrintProduct.query.filter_by(sku=sku).first():
                result.status = False
                result.error = 'SKU already exists'
                return result

            new_product = PrintProduct(
                name=name,
                sku=sku,
                description=description,
                image=image,
                category_id=category.id,
                type_id=int(type_id) if int(type_id) > 0 else 0,
                vendor_id=vendor.id,
                vendor_product_id=vendor_product_id,
            )
            db.session.add(new_product)
            db.session.commit()

            PrintProductController.update_category_classification_status(category.id)

            result.status = True
            result.data = new_product.to_dict()
            return result
        except Exception as e:
            db.session.rollback()
            result.status = False
            result.error = f'Failed to create product: {str(e)}'
            logger.error('Error creating manual product: %s', e)
            return result

    @staticmethod
    def ensure_default_product_types_for_categories(default_suffix: str = "General") -> Result:
        """Ensure each category has at least one product type.

        Creates one default product type for categories that currently have none.
        """
        result = Result()

        try:
            categories = PrintProductCategory.query.all()
            created = []

            for category in categories:
                has_types = PrintProductType.query.filter_by(category_id=category.id).first() is not None
                if has_types:
                    continue

                candidate_name = f"{category.name} {default_suffix}".strip()
                # Guard against per-category name collisions.
                if PrintProductType.query.filter_by(category_id=category.id, name=candidate_name).first():
                    candidate_name = f"{category.name} Default"

                new_type = PrintProductType(
                    name=candidate_name,
                    category_id=category.id,
                    description=f"Default product type for {category.name}",
                    image=None,
                )
                db.session.add(new_type)
                created.append(category.id)

            if created:
                db.session.commit()
            else:
                db.session.rollback()

            result.status = True
            result.data = {
                "message": "Default product type bootstrap completed",
                "categories_scanned": len(categories),
                "categories_updated": len(created),
            }
        except Exception as e:
            db.session.rollback()
            result.status = False
            result.error = f"Failed to ensure default product types: {str(e)}"
            logger.error("Error ensuring default product types: %s", e)

        return result

    @staticmethod
    def enable_all_categories_if_none_enabled() -> Result:
        """Enable all categories only when none are currently enabled."""
        result = Result()

        try:
            categories = PrintProductCategory.query.all()
            if not categories:
                result.status = True
                result.data = {
                    "message": "No categories found",
                    "categories_total": 0,
                    "categories_enabled": 0,
                    "categories_updated": 0,
                }
                return result

            currently_enabled = [c for c in categories if c.enabled]
            if currently_enabled:
                result.status = True
                result.data = {
                    "message": "At least one category is already enabled; no changes made",
                    "categories_total": len(categories),
                    "categories_enabled": len(currently_enabled),
                    "categories_updated": 0,
                }
                return result

            for category in categories:
                category.enabled = True

            db.session.commit()
            result.status = True
            result.data = {
                "message": "Enabled all categories because none were enabled",
                "categories_total": len(categories),
                "categories_enabled": len(categories),
                "categories_updated": len(categories),
            }
        except Exception as e:
            db.session.rollback()
            result.status = False
            result.error = f"Failed to enable categories: {str(e)}"
            logger.error("Error enabling categories: %s", e)

        return result

    @staticmethod
    def get_all_product_categories() -> Result:
        """Retrieve all product categories from the database."""

        result = Result()

        table_is_empty = (PrintProductCategory.query.first() is None)
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

        table_is_empty = (PrintProductCategory.query.first() is None)
        if(table_is_empty):
            result.data = []
            return result

        logger.info("Fetching enabled categories ... ")
        categories = PrintProductCategory.query.filter_by(enabled=True).all()
       
        num_categories = len(categories)
        if num_categories == 1:
            logger.info("Found %s enabled category ... ", num_categories)
            result.data = [categories[0].to_dict()]
        else:
            logger.info("Found %s enabled categories ... ", num_categories)
            result.data = [category.to_dict() for category in categories]
        
        return result

    @staticmethod
    def update_print_product_category_status(category_id: int, enabled: bool):
        """Enable or disable a category."""
        result = Result()

        try:
            table_is_empty = (PrintProductCategory.query.first() is None)
            if table_is_empty:
                result.data = []
                return result

            # Fetch the category by ID
            category = db.session.get(PrintProductCategory, category_id)
            if not category:
                logger.warning("Category with ID %s not found.", category_id)
                result.status = False
                result.error = PrintProductErrors.PRINT_PRODUCT_CATEGORY_NOT_FOUND.value
                return result

            # Update category status
            category.enabled = enabled
            db.session.commit()  

            result.data = {"message": PrintProductSuccessMessages.UPDATED_PRINT_PRODUCT_CATEGORY_STATUS_SUCCESSFULLY.value}
        
        except Exception as e:
            logger.error("Failed to update category status: %s", e)
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
            logger.error("Failed to fetch categories from Sinalite API: %s", e)
            result.data = {"message": "Failed to sync product categories"}
            return result

        logger.info("Fetching all product categories currently known ...")
        try:
            existing_categories = {
                category.name for category in PrintProductCategory.query.with_entities(PrintProductCategory.name).all()
            }
        except Exception as e:
            logger.error("Failed to fetch existing product categories: %s", e)
            result.data = {"message": "Failed to sync product categories"}
            return result

        new_categories = [
            PrintProductCategory(name=name) for name in sinalite_categories if name not in existing_categories
        ]

        logger.info(
            "Found %s new %s ...",
            len(new_categories),
            "category" if len(new_categories) == 1 else "categories",
        )

        if new_categories:
            logger.info("Syncing product categories ...")
            try:
                db.session.bulk_save_objects(new_categories) 
                db.session.commit() 
                logger.info("Synced product categories successfully ...")
            except Exception as e:
                logger.error("Failed to sync new product categories: %s", e)
                db.session.rollback()  # ✅ Rollback in case of failure
                result.data = {"message": "Failed to sync product categories"}
                return result

        result.data = {"message": PrintProductSuccessMessages.PRINT_PRODUCT_CATEGORY_IN_SYNC.value}
        return result

    @staticmethod
    def get_all_vendors() -> Result:
        """Retrieve all vendors from the database."""
        result = Result()

        try:
            from server.models.print_product import Vendor
            
            # Check if table is empty
            table_is_empty = (Vendor.query.first() is None)
            if table_is_empty:
                result.data = []
                result.status = True
                return result

            # Fetch all vendors sorted by name
            vendors = Vendor.query.order_by(Vendor.name.asc()).all()

            if vendors:
                result.data = [vendor.to_dict() for vendor in vendors]
                result.status = True
            else:
                result.status = False
                result.error = "Failed to fetch vendors"
            
        except Exception as e:
            result.status = False
            result.error = f"Failed to fetch vendors: {str(e)}"
            logger.error("Error fetching vendors: %s", e)

        return result

    @staticmethod
    def sync_print_products(category_id: int) -> Result:
        """Sync print products from Sinalite API for a given category (manual trigger)."""
        result = Result()
        
        try:
            # Validate category exists
            category = db.session.get(PrintProductCategory, category_id)
            if not category:
                result.status = False
                result.error = PrintProductErrors.PRINT_PRODUCT_CATEGORY_NOT_FOUND.value
                return result
            
            # Get products from Sinalite API for this category
            sinalite_products = sinalite.get_products()
            if not sinalite_products:
                result.status = False
                result.error = PrintProductErrors.FAILED_TO_FETCH_PRINT_PRODUCTS.value
                return result
            
            # Filter products for this category
            category_products = [
                product for product in sinalite_products 
                if product.get('category') == category.name
            ]
            
            if not category_products:
                result.data = {
                    "message": "No products found in Sinalite for this category",
                    "products_added": 0,
                    "products_updated": 0,
                    "total_products": 0
                }
                result.status = True
                return result
            
            # Get existing products in our database for this category
            existing_products = PrintProduct.query.filter_by(category_id=category_id).all()
            existing_sku_map = {product.sku: product for product in existing_products}

            # If this category has exactly one non-system type, use it as the
            # default assignment target for unclassified products.
            category_types = PrintProductType.query.filter(
                PrintProductType.category_id == category_id,
                PrintProductType.id != 0,
            ).order_by(PrintProductType.id.asc()).all()
            default_type_id = category_types[0].id if len(category_types) == 1 else None
            
            # Sinalite vendor ID is 1 (as defined in the migration)
            SINALITE_VENDOR_ID = 1
            
            products_added = 0
            products_updated = 0
            
            for sinalite_product in category_products:
                sku = sinalite_product.get('sku')
                if not sku:
                    continue  # Skip products without SKU
                
                if sku in existing_sku_map:
                    # Update existing product - only update name, keep existing description
                    existing_product = existing_sku_map[sku]
                    existing_product.name = sinalite_product.get('name', existing_product.name)
                    # Note: We don't update description from Sinalite since they don't provide descriptions
                    # Update vendor_product_id if it changed
                    if existing_product.vendor_product_id != str(sinalite_product.get('id')):
                        existing_product.vendor_product_id = str(sinalite_product.get('id'))
                    if default_type_id and existing_product.type_id == 0:
                        existing_product.type_id = default_type_id
                    products_updated += 1
                else:
                    # Create new product - set description to None initially
                    new_product = PrintProduct(
                        name=sinalite_product.get('name', ''),
                        sku=sku,
                        description=None,  # Sinalite doesn't provide descriptions, user will define later
                        category_id=category_id,
                        type_id=default_type_id or 0,
                        vendor_id=SINALITE_VENDOR_ID,  # Sinalite vendor
                        vendor_product_id=str(sinalite_product.get('id'))  # Sinalite's product ID
                    )
                    db.session.add(new_product)
                    products_added += 1
            
            # Commit all changes
            db.session.commit()
            
            # Update category classification status after sync
            PrintProductController.update_category_classification_status(category_id)
            
            result.data = {
                "message": PrintProductSuccessMessages.PRINT_PRODUCTS_SYNCED_SUCCESSFULLY.value,
                "products_added": products_added,
                "products_updated": products_updated,
                "total_products": len(category_products)
            }
            result.status = True
            
        except Exception as e:
            db.session.rollback()
            result.status = False
            result.error = f"Failed to sync print products: {str(e)}"
            logger.error("Error syncing print products for category %s: %s", category_id, e)
        
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
    def get_all_products_by_category(category_id: int) -> Result:
        """Fetch print products from database by category ID, regardless of enabled status"""
        result = Result()

        table_is_empty = (PrintProductCategory.query.first() is None)
        if(table_is_empty):
            result.data = []
            return result
        
        # Validate category exists (regardless of enabled status)
        local_category = db.session.get(PrintProductCategory, category_id)
        if not local_category:
            result.status = False
            result.error = PrintProductErrors.PRINT_PRODUCT_CATEGORY_NOT_FOUND.value
            return result

        # Get products for this category
        db_products = PrintProduct.query.filter_by(category_id=category_id).order_by(PrintProduct.name.asc()).all()
        logger.debug(
            "Found %s products for category %s", len(db_products), category_id
        )
        
        # Log each product's type_id
        for product in db_products:
            logger.debug(
                "Product %s (%s) has type_id: %s",
                product.id,
                product.name,
                product.type_id,
            )
        
        # Convert to dictionary format to maintain API compatibility
        filtered_products = [product.to_dict() for product in db_products]

        logger.debug("Filtered products: %s", filtered_products)

        # Always return a list even if empty
        result.data = filtered_products

        return result

    @staticmethod
    def get_enabled_products_by_category(category_id: int) -> Result:
        """Fetch print products from database by category ID, ensuring category is enabled"""
        result = Result()

        # Two conditions for a product to be considered enabled
        # 1. The category must be enabled in the database
        # 2. The product must be present in the database

        table_is_empty = (PrintProductCategory.query.first() is None)
        if(table_is_empty):
            result.data = []
            return result

        # Validate category exists and is enabled in the database
        local_category = db.session.get(PrintProductCategory, category_id)
        if not local_category or not local_category.enabled:
            result.status = False
            result.error = PrintProductErrors.PRINT_PRODUCT_CATEGORY_NOT_FOUND.value
            return result
        
        # Get products from database for this category
        db_products = PrintProduct.query.filter_by(category_id=category_id).order_by(PrintProduct.name.asc()).all()
        
        # Convert to dictionary format to maintain API compatibility
        filtered_products = [product.to_dict() for product in db_products]

        # Always return a list even if empty
        result.data = filtered_products

        return result

    @staticmethod
    def get_products_by_type(type_id: int) -> Result:
        """Fetch print products from database by product type ID."""
        result = Result()

        try:
            # Validate product type exists
            product_type = db.session.get(PrintProductType, type_id)
            if not product_type:
                result.status = False
                result.error = PrintProductErrors.PRINT_PRODUCT_TYPE_NOT_FOUND.value
                return result

            # Get products for this type
            products = PrintProduct.query.filter_by(type_id=type_id).order_by(PrintProduct.name.asc()).all()
            
            # Convert to dictionary format
            result.data = [product.to_dict() for product in products]
            result.status = True

        except Exception as e:
            result.status = False
            result.error = f"Failed to fetch products by type: {str(e)}"
            logger.error("Error fetching products by type %s: %s", type_id, e)

        return result

    @staticmethod
    def update_print_product_category(category_id: int, description: str = None, image=None) -> Result:
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
            if image is not None:
                if isinstance(image, FileStorage):
                    # Ensure file is not empty
                    if image.filename == "":
                        result.status = False
                        result.error = PrintProductErrors.EMPTY_IMAGE_FILENAME.value
                        return result

                    # Validate file type
                    content_type = image.content_type
                    if not content_type or not content_type.startswith('image/'):
                        result.status = False
                        result.error = PrintProductErrors.INVALID_IMAGE_FILE.value
                        return result

                    # Generate unique filename to avoid conflicts
                    original_filename = secure_filename(image.filename)
                    file_extension = os.path.splitext(original_filename)[1].lower()
                    
                    # Generate unique filename with timestamp and UUID
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    unique_id = str(uuid.uuid4())[:8]
                    unique_filename = f"category_{timestamp}_{unique_id}{file_extension}"
                    
                    # Read file data
                    file_data = image.read()

                    # Upload file using current filestorage
                    filestorage = current_app.extensions["filestorage"]
                    image_url = filestorage.upload_file(file_data, unique_filename, content_type)

                    # Save URL in DB
                    category.image = image_url
                    
                    logger.info(
                        "Category image updated successfully: %s -> %s",
                        unique_filename,
                        image_url,
                    )
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

    @staticmethod
    def get_all_print_product_types() -> Result:
        """Retrieve all print product types from the database."""
        result = Result()

        try:
            # Check if table is empty
            table_is_empty = (PrintProductType.query.first() is None)
            if table_is_empty:
                result.data = []
                result.status = True
                return result

            # Fetch all product types sorted by name
            product_types = PrintProductType.query.order_by(PrintProductType.name.asc()).all()

            if product_types:
                result.data = [product_type.to_dict() for product_type in product_types]
                result.status = True
            else:
                result.status = False
                result.error = PrintProductErrors.FAILED_TO_FETCH_PRINT_PRODUCT_TYPES.value
            
        except Exception as e:
            result.status = False
            result.error = f"{PrintProductErrors.FAILED_TO_FETCH_PRINT_PRODUCT_TYPES.value}: {str(e)}"
            logger.error("Error fetching print product types: %s", e)

        
        return result

    @staticmethod
    def get_product_types_by_category(category_id: int) -> Result:
        """Retrieve product types for a specific category."""
        result = Result()

        try:
            # Validate category exists
            category = db.session.get(PrintProductCategory, category_id)
            if not category:
                result.error = PrintProductErrors.PRINT_PRODUCT_CATEGORY_NOT_FOUND.value
                result.status = False
                return result

            # Fetch product types for this category, sorted by name
            product_types = PrintProductType.query.filter_by(category_id=category_id).order_by(PrintProductType.name.asc()).all()

            if product_types:
                result.data = [product_type.to_dict() for product_type in product_types]
                result.status = True
            else:
                result.data = []
                result.status = True
        except Exception as e:
            result.error = f"{PrintProductErrors.FAILED_TO_FETCH_PRINT_PRODUCT_TYPES.value}: {str(e)}"
            logger.error("Error fetching product types for category %s: %s", category_id, e)

        return result

    @staticmethod
    def create_print_product_type(data: dict) -> Result:
        """Create a new print product type in the database."""
        result = Result()
        
        try:
            # Extract fields from input data
            name = data.get('name')
            category_id = data.get('category_id')
            description = data.get('description')
            image = data.get('image')

            # Validate required fields
            if not name:
                result.status = False
                result.error = PrintProductErrors.PRODUCT_TYPE_NAME_REQUIRED.value
                return result
            
            if not category_id:
                result.status = False
                result.error = PrintProductErrors.PRODUCT_TYPE_CATEGORY_ID_REQUIRED.value
                return result
                
            if not description:
                result.status = False
                result.error = PrintProductErrors.PRODUCT_TYPE_DESCRIPTION_REQUIRED.value
                return result
            
            # Validate name length
            if len(name) < 2:
                result.status = False
                result.error = PrintProductErrors.PRODUCT_TYPE_NAME_TOO_SHORT.value
                return result
                
            if len(name) > 255:
                result.status = False
                result.error = PrintProductErrors.PRODUCT_TYPE_NAME_TOO_LONG.value
                return result
            
            # Validate category exists
            category = db.session.get(PrintProductCategory, category_id)
            if not category:
                result.status = False
                result.error = PrintProductErrors.PRODUCT_TYPE_CATEGORY_NOT_FOUND.value
                return result

            # Check if product type with same name already exists in this category
            existing_type = PrintProductType.query.filter_by(
                name=name, 
                category_id=category_id
            ).first()
            
            if existing_type:
                result.status = False
                result.error = PrintProductErrors.PRODUCT_TYPE_NAME_ALREADY_EXISTS.value
                return result

            # Handle image upload if provided
            image_url = None
            if image is not None:
                if isinstance(image, FileStorage):
                    # Ensure file is not empty
                    if image.filename == "":
                        result.status = False
                        result.error = PrintProductErrors.EMPTY_IMAGE_FILENAME.value
                        return result

                    # Validate file type
                    content_type = image.content_type
                    if not content_type or not content_type.startswith('image/'):
                        result.status = False
                        result.error = PrintProductErrors.INVALID_IMAGE_FILE.value
                        return result

                    # Generate unique filename to avoid conflicts
                    import uuid
                    from werkzeug.utils import secure_filename
                    from datetime import datetime
                    
                    # Get file extension
                    original_filename = secure_filename(image.filename)
                    file_extension = os.path.splitext(original_filename)[1].lower()
                    
                    # Generate unique filename with timestamp and UUID
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    unique_id = str(uuid.uuid4())[:8]
                    unique_filename = f"product_type_{timestamp}_{unique_id}{file_extension}"
                    
                    # Read file data
                    file_data = image.read()
                    
                    # Upload file using filestorage
                    filestorage = current_app.extensions["filestorage"]
                    image_url = filestorage.upload_file(file_data, unique_filename, content_type)
                    
                    logger.info("Image uploaded successfully: %s -> %s", unique_filename, image_url)
                else:
                    result.status = False
                    result.error = PrintProductErrors.INVALID_IMAGE_FILE.value
                    return result

            # Create new product type
            new_product_type = PrintProductType(
                name=name,
                category_id=category_id,
                description=description,
                image=image_url
            )
            
            db.session.add(new_product_type)
            db.session.commit()
            
            result.data = new_product_type.to_dict()
            result.status = True
            
        except Exception as e:
            db.session.rollback()
            result.status = False
            result.error = f"{PrintProductErrors.FAILED_TO_CREATE_PRODUCT_TYPE.value}: {str(e)}"
            logger.error("Error creating product type: %s", e)

        return result

    @staticmethod
    def update_print_product_type(type_id: int, description: str = None, image=None) -> Result:
        """Update the description or image of a product type securely"""
        result = Result()

        try:
            product_type = db.session.get(PrintProductType, type_id)

            if not product_type:
                result.status = False
                result.error = PrintProductErrors.PRINT_PRODUCT_TYPE_NOT_FOUND.value
                return result

            # Prevent modification of the unclassified wildcard type (ID 0)
            if type_id == 0:
                result.status = False
                result.error = "Cannot modify the unclassified product type (system reserved)"
                return result

            # Sanitize and validate description
            if description:
                description = escape(description.strip())
                if len(description) > 1000:
                    result.status = False
                    result.error = PrintProductErrors.PRINT_PRODUCT_DESCRIPTION_TOO_LONG.value
                    return result
                product_type.description = description

            # Handle image upload
            if image is not None:
                if isinstance(image, FileStorage):
                    # Ensure file is not empty
                    if image.filename == "":
                        result.status = False
                        result.error = PrintProductErrors.EMPTY_IMAGE_FILENAME.value
                        return result

                    # Validate file type
                    content_type = image.content_type
                    if not content_type or not content_type.startswith('image/'):
                        result.status = False
                        result.error = PrintProductErrors.INVALID_IMAGE_FILE.value
                        return result

                    # Generate unique filename to avoid conflicts
                    original_filename = secure_filename(image.filename)
                    file_extension = os.path.splitext(original_filename)[1].lower()
                    
                    # Generate unique filename with timestamp and UUID
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    unique_id = str(uuid.uuid4())[:8]
                    unique_filename = f"product_type_{timestamp}_{unique_id}{file_extension}"
                    
                    # Read file data
                    file_data = image.read()

                    # Upload file using current filestorage
                    filestorage = current_app.extensions["filestorage"]
                    image_url = filestorage.upload_file(file_data, unique_filename, content_type)

                    # Save URL in DB
                    product_type.image = image_url
                    
                    logger.info(
                        "Product type image updated successfully: %s -> %s",
                        unique_filename,
                        image_url,
                    )
                else:
                    result.status = False
                    result.error = PrintProductErrors.INVALID_IMAGE_FILE.value
                    return result

            db.session.commit()
            result.data = {"message": PrintProductSuccessMessages.PRODUCT_TYPE_UPDATED_SUCCESSFULLY.value}

        except Exception as e:
            db.session.rollback()
            result.status = False
            result.error = f"{PrintProductErrors.FAILED_TO_UPDATE_PRODUCT_TYPE.value}: {str(e)}"

        return result

    @staticmethod
    def delete_print_product_type(type_id: int) -> Result:
        """Delete a print product type from the database."""
        result = Result()

        try:
            product_type = db.session.get(PrintProductType, type_id)

            if not product_type:
                result.status = False
                result.error = PrintProductErrors.PRINT_PRODUCT_TYPE_NOT_FOUND.value
                return result

            # Prevent deletion of the unclassified wildcard type (ID 0)
            if type_id == 0:
                result.status = False
                result.error = "Cannot delete the unclassified product type (system reserved)"
                return result

            # Check if there are any products using this type
            products_using_type = PrintProduct.query.filter_by(type_id=type_id).first()
            
        
            if products_using_type:
                result.status = False
                result.error = PrintProductErrors.PRODUCT_TYPE_IN_USE.value
                return result

            # Delete the product type
            db.session.delete(product_type)
            db.session.commit()

            result.data = {"message": PrintProductSuccessMessages.PRODUCT_TYPE_DELETED_SUCCESSFULLY.value}
            result.status = True

        except Exception as e:
            db.session.rollback()
            result.status = False
            result.error = f"{PrintProductErrors.FAILED_TO_DELETE_PRODUCT_TYPE.value}: {str(e)}"
            logger.error("Error deleting product type: %s", e)

        return result

    @staticmethod
    def ensure_unclassified_type_exists() -> Result:
        """Ensure the unclassified product type (ID 0) exists in the database"""
        result = Result()

        try:
            # Check if unclassified type already exists
            unclassified_type = db.session.get(PrintProductType, 0)
            
            if not unclassified_type:
                # Create the unclassified type
                unclassified_type = PrintProductType(
                    id=0,
                    name="Unclassified",
                    description="Default type for products not yet classified",
                    category_id=None  # No specific category - system-wide wildcard
                )
                
                db.session.add(unclassified_type)
                db.session.commit()
                
                result.data = {"message": "Unclassified product type created successfully"}
                result.status = True
            else:
                result.data = {"message": "Unclassified product type already exists"}
                result.status = True

        except Exception as e:
            db.session.rollback()
            result.status = False
            result.error = f"Failed to ensure unclassified type exists: {str(e)}"
            logger.error("Error ensuring unclassified type exists: %s", e)

        return result

    @staticmethod
    def assign_product_to_type(product_id: int, type_id: int) -> Result:
        """Assign a product to a product type"""
        result = Result()
        
        try:
            # Get the product
            product = db.session.get(PrintProduct, product_id)
            
            if not product:
                result.status = False
                result.error = "Product not found"
                return result

            # Prevent assignment to the unclassified wildcard type (ID 0)
            if type_id == 0:
                result.status = False
                result.error = "Cannot assign product to unclassified type (use unassign instead)"
                return result

            # Get the product type
            product_type = db.session.get(PrintProductType, type_id)
            logger.debug(
                "Found product type %s: %s",
                type_id,
                product_type.name if product_type else "NOT FOUND",
            )

            if not product_type:
                result.status = False
                result.error = "Product type not found"
                return result

            # Verify the product type belongs to the same category as the product
            if product_type.category_id != product.category_id:
                result.status = False
                result.error = "Product type must belong to the same category as the product"
                return result

            # Assign the product to the type
            old_type_id = product.type_id
            product.type_id = type_id
            logger.debug(
                "Updating product %s type_id from %s to %s",
                product_id,
                old_type_id,
                type_id,
            )
            
            db.session.commit()
            logger.debug("Product type assignment committed for product %s", product_id)
            
            # Verify the update
            db.session.refresh(product)
            logger.debug(
                "After commit, product %s type_id: %s",
                product_id,
                product.type_id,
            )

            # Update the category's classification status
            PrintProductController.update_category_classification_status(product.category_id)

            result.data = {"message": "Product assigned to product type successfully"}
            result.status = True

        except Exception as e:
            db.session.rollback()
            result.status = False
            result.error = f"Failed to assign product to type: {str(e)}"
            logger.error("Error assigning product to type: %s", e)

        return result

    @staticmethod
    def unassign_product_from_type(product_id: int) -> Result:
        """Unassign a product from its product type"""
        result = Result()

        try:
            # Get the product
            product = db.session.get(PrintProduct, product_id)
            
            if not product:
                result.status = False
                result.error = "Product not found"
                return result

            # Store category_id before unassigning
            category_id = product.category_id

            # Unassign the product from its type (set to unclassified type 0)
            product.type_id = 0
            db.session.commit()

            # Update the category's classification status
            PrintProductController.update_category_classification_status(category_id)

            result.data = {"message": "Product unassigned from product type successfully"}
            result.status = True

        except Exception as e:
            db.session.rollback()
            result.status = False
            result.error = f"Failed to unassign product from type: {str(e)}"
            logger.error("Error unassigning product from type: %s", e)

        return result

    @staticmethod
    def update_print_product(product_id: int, description: str = None, image=None) -> Result:
        """Update the description or image of a product securely"""
        result = Result()

        try:
            product = db.session.get(PrintProduct, product_id)

            if not product:
                result.status = False
                result.error = "Product not found"
                return result

            # Sanitize and validate description
            if description:
                description = escape(description.strip())
                if len(description) > 1000:
                    result.status = False
                    result.error = PrintProductErrors.PRINT_PRODUCT_DESCRIPTION_TOO_LONG.value
                    return result
                product.description = description

            # Handle image upload
            if image is not None:
                if isinstance(image, FileStorage):
                    # Ensure file is not empty
                    if image.filename == "":
                        result.status = False
                        result.error = PrintProductErrors.EMPTY_IMAGE_FILENAME.value
                        return result

                    # Validate file type
                    content_type = image.content_type
                    if not content_type or not content_type.startswith('image/'):
                        result.status = False
                        result.error = PrintProductErrors.INVALID_IMAGE_FILE.value
                        return result

                    # Generate unique filename to avoid conflicts
                    original_filename = secure_filename(image.filename)
                    file_extension = os.path.splitext(original_filename)[1].lower()
                    
                    # Generate unique filename with timestamp and UUID
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    unique_id = str(uuid.uuid4())[:8]
                    unique_filename = f"product_{timestamp}_{unique_id}{file_extension}"
                    
                    # Read file data
                    file_data = image.read()

                    # Upload file using current filestorage
                    filestorage = current_app.extensions["filestorage"]
                    image_url = filestorage.upload_file(file_data, unique_filename, content_type)

                    # Save URL in DB
                    product.image = image_url
                    
                    logger.info("Product image updated successfully: %s -> %s", unique_filename, image_url)
                else:
                    result.status = False
                    result.error = PrintProductErrors.INVALID_IMAGE_FILE.value
                    return result

            db.session.commit()
            result.data = {"message": "Product updated successfully"}

        except Exception as e:
            db.session.rollback()
            result.status = False
            result.error = f"Failed to update product: {str(e)}"

        return result

    @staticmethod
    def are_all_products_classified(category_id: int) -> Result:
        """Check if all products in a category are classified to a product type"""
        result = Result()

        try:
            total_products = PrintProduct.query.filter_by(category_id=category_id).count()

            if total_products == 0:
                # No products in category, so technically all are classified
                result.data = {"all_classified": True, "total_products": 0, "classified_products": 0}
                result.status = True
                return result

            classified_products = PrintProduct.query.filter(
                PrintProduct.category_id == category_id,
                PrintProduct.type_id > 0,
            ).count()
            all_classified = classified_products == total_products

            result.data = {
                "all_classified": all_classified,
                "total_products": total_products,
                "classified_products": classified_products,
                "unclassified_products": total_products - classified_products
            }
            result.status = True

        except Exception as e:
            result.status = False
            result.error = f"Failed to check product classification: {str(e)}"
            logger.error("Error checking product classification: %s", e)

        return result

    @staticmethod
    def update_category_classification_status(category_id: int) -> Result:
        """Update the classification status for a specific category"""
        result = Result()

        try:
            from server.models.print_product import PrintProduct
            
            # Get the category
            category = db.session.get(PrintProductCategory, category_id)
            if not category:
                result.status = False
                result.error = "Category not found"
                return result

            total_products = PrintProduct.query.filter_by(category_id=category_id).count()

            if total_products == 0:
                # No products in category, so all are classified
                category.product_classification_status = {
                    "all_classified": True,
                    "total_products": 0,
                    "classified_products": 0,
                    "unclassified_products": 0
                }
            else:
                classified_products = PrintProduct.query.filter(
                    PrintProduct.category_id == category_id,
                    PrintProduct.type_id > 0,
                ).count()
                all_classified = classified_products == total_products

                category.product_classification_status = {
                    "all_classified": all_classified,
                    "total_products": total_products,
                    "classified_products": classified_products,
                    "unclassified_products": total_products - classified_products
                }

            db.session.commit()
            result.status = True

        except Exception as e:
            db.session.rollback()
            result.status = False
            result.error = f"Failed to update classification status: {str(e)}"
            logger.error("Error updating classification status: %s", e)

        return result

    @staticmethod
    def get_all_product_categories_with_status() -> Result:
        """Retrieve all product categories with their classification status"""
        result = Result()

        try:
            # Check if table is empty
            table_is_empty = (PrintProductCategory.query.first() is None)
            if table_is_empty:
                result.data = []
                return result

            # Always fetch categories sorted by name
            categories = PrintProductCategory.query.order_by(PrintProductCategory.name.asc()).all()

            if categories:
                result.data = [category.to_dict() for category in categories]
            else:
                result.status = False
                result.error = PrintProductErrors.FAILED_TO_FETCH_PRINT_PRODUCT_CATEGORIES.value
            
        except Exception as e:
            result.status = False
            result.error = f"{PrintProductErrors.FAILED_TO_FETCH_PRINT_PRODUCT_CATEGORIES.value}: {str(e)}"
            logger.error("Error fetching categories with status: %s", e)

        return result