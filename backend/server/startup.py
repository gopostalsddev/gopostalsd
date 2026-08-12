"""Explicit application-data bootstrap and database health utilities.

Alembic owns schema creation.  Nothing in this module is called automatically
while the Flask application starts.
"""
import logging
import os
from sqlalchemy import inspect, text
from server import database as db
from server.controllers.print_product_controller import PrintProductController
from server.models.pricing import PricingPolicy
from server.services.role_service import RoleService

logger = logging.getLogger(__name__)

REQUIRED_BOOTSTRAP_TABLES = {
    "pricing_policies",
    "print_product_categories",
    "print_product_types",
    "permissions",
    "roles",
}


def _require_migrated_schema() -> None:
    """Refuse to bootstrap data until Alembic has created the required schema."""
    inspector = inspect(db.engine)
    missing = sorted(
        table for table in REQUIRED_BOOTSTRAP_TABLES
        if not inspector.has_table(table)
    )
    if missing:
        raise RuntimeError(
            "Database schema is not migrated; missing table(s): "
            + ", ".join(missing)
            + ". Run `flask db upgrade` first."
        )


def bootstrap_required_data(*, enable_categories_if_none: bool = False) -> dict:
    """Initialize required application data after Alembic has completed.

    This function performs no DDL and is deliberately invoked by a CLI command,
    never by application startup.  Repeated calls are safe.
    """
    _require_migrated_schema()

    from server.models.print_product import PrintProductType

    # ID 0 is migration-owned state.  Recreating it here would conceal a broken
    # or incomplete migration, so bootstrap verifies it instead.
    unclassified_type = db.session.get(PrintProductType, 0)
    if unclassified_type is None:
        raise RuntimeError(
            "Migration-owned unclassified product type (ID 0) is missing. "
            "Do not repair it at runtime; verify the Alembic history."
        )

    default_types_result = (
        PrintProductController.ensure_default_product_types_for_categories()
    )
    if not default_types_result.status:
        raise RuntimeError(default_types_result.error)

    # Authentication depends on these system roles, including the one-time
    # production-admin command. Seed missing entries explicitly here rather
    # than hiding data mutation in application startup or read operations.
    RoleService()._initialize_default_roles()

    categories_result = None
    if enable_categories_if_none:
        categories_result = (
            PrintProductController.enable_all_categories_if_none_enabled()
        )
        if not categories_result.status:
            raise RuntimeError(categories_result.error)

    pricing_policy_created = False
    if PricingPolicy.get_current() is None:
        db.session.add(PricingPolicy())
        db.session.commit()
        pricing_policy_created = True

    return {
        "unclassified_type_verified": True,
        "default_product_types": default_types_result.data,
        "system_roles_verified": True,
        "categories": categories_result.data if categories_result else None,
        "pricing_policy_created": pricing_policy_created,
    }


def ensure_database_structures():
    """Deprecated compatibility wrapper; performs data bootstrap only, no DDL."""
    logger.warning(
        "ensure_database_structures() is deprecated; use the explicit "
        "`flask bootstrap-data` command after migrations"
    )
    try:
        bootstrap_required_data(
            enable_categories_if_none=(
                os.getenv("AUTO_ENABLE_CATEGORIES_WHEN_NONE", "false").lower()
                == "true"
            )
        )
        return True
    except Exception:
        db.session.rollback()
        logger.exception("Explicit application-data bootstrap failed")
        return False

def verify_database_health():
    """
    Verify that the database is healthy and accessible.
    This can be called during health checks or startup.
    """
    try:
        # Simple database connectivity test
        db.session.execute(text("SELECT 1"))
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
        # Check table presence via SQLAlchemy inspection (SQLAlchemy 2.x safe).
        inspector = inspect(db.engine)
        if not inspector.has_table('print_product_types'):
            logger.info("📋 Database tables don't exist yet: print_product_types table missing")
            return False

        logger.info("✅ Database tables exist")
        return True
    except Exception as e:
        logger.info(f"📋 Database tables don't exist yet: {str(e)}")
        return False
