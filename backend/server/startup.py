"""
Server startup utilities for ensuring database structures and data are properly initialized.
"""
import logging
import os
from server import database as db
from server.controllers.print_product_controller import PrintProductController

logger = logging.getLogger(__name__)

def ensure_database_structures():
    """
    Ensure all necessary database structures and data exist on server startup.
    This function is called during server initialization to set up the database properly.
    """
    logger.info("🔧 Ensuring database structures are properly initialized...")
    
    try:
        # First check if database tables exist
        if not check_database_tables_exist():
            logger.warning("⚠️ Database tables don't exist yet. Please run migrations first.")
            logger.info("💡 Run: python scripts/setup_unclassified_system.py")
            return False
        
        # Ensure unclassified product type exists
        logger.info("📋 Checking for unclassified product type...")
        result = PrintProductController.ensure_unclassified_type_exists()
        
        if result.status:
            logger.info(f"✅ {result.data['message']}")
        else:
            logger.warning(f"⚠️ Warning: {result.error}")
            
        # Verify the unclassified type was created successfully
        try:
            from server.models.print_product import PrintProductType
            unclassified_type = db.session.get(PrintProductType, 0)
            if unclassified_type:
                logger.info(f"✅ Verified unclassified type exists: {unclassified_type.name} (ID: {unclassified_type.id})")
            else:
                logger.error("❌ Unclassified type verification failed - type not found in database")
                return False
        except Exception as e:
            logger.error(f"❌ Error verifying unclassified type: {str(e)}")
            return False

        logger.info("📋 Ensuring default product types for categories...")
        default_types_result = PrintProductController.ensure_default_product_types_for_categories()
        if default_types_result.status:
            logger.info("✅ %s", default_types_result.data.get("message", "Default type bootstrap completed"))
        else:
            logger.warning("⚠️ Failed to ensure default product types: %s", default_types_result.error)

        auto_enable_when_none = os.getenv("AUTO_ENABLE_CATEGORIES_WHEN_NONE", "true").lower() == "true"
        if auto_enable_when_none:
            logger.info("📋 Ensuring at least one category is enabled...")
            enable_result = PrintProductController.enable_all_categories_if_none_enabled()
            if enable_result.status:
                logger.info("✅ %s", enable_result.data.get("message", "Category enable check completed"))
            else:
                logger.warning("⚠️ Failed to ensure enabled categories: %s", enable_result.error)
            
        # Add more database structure checks here as needed
        # For example:
        # - Ensure default categories exist
        # - Verify database schema version
        # - Check for required indexes
        
        logger.info("✅ Database structure initialization completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error during database structure initialization: {str(e)}")
        # Don't fail server startup for this, just log the error
        return False

def verify_database_health():
    """
    Verify that the database is healthy and accessible.
    This can be called during health checks or startup.
    """
    try:
        # Simple database connectivity test
        db.session.execute("SELECT 1")
        logger.info("✅ Database connection verified")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {str(e)}")
        return False

def check_database_tables_exist():
    """
    Check if the required database tables exist.
    Returns True if tables exist, False if they need to be created.
    """
    try:
        # Check if the main tables exist by trying to query them
        from server.models.print_product import PrintProductType
        db.session.execute("SELECT COUNT(*) FROM print_product_types LIMIT 1")
        logger.info("✅ Database tables exist")
        return True
    except Exception as e:
        logger.info(f"📋 Database tables don't exist yet: {str(e)}")
        return False 