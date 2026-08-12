import logging
import os

from flask import Flask

from server.config import database
from server.models.auth import Address, Role, User, UserStatus
from server.services.password_service import PasswordService

logger = logging.getLogger(__name__)

DEFAULT_STREET = "1501 India St Suite 103"
DEFAULT_CITY = "San Diego"
DEFAULT_STATE = "CA"


def ensure_production_admin(app: Flask) -> bool:
    """Create the configured Admin when explicitly invoked after migrations."""
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")

    if not admin_email or not admin_password:
        return False

    try:
        admin_role = Role.query.filter_by(name="Admin").first()
        if not admin_role:
            logger.warning(
                "Admin role not found; skipping production admin bootstrap. "
                "Run database migrations first."
            )
            return False

        default_address = Address.query.filter_by(
            street=DEFAULT_STREET,
            city=DEFAULT_CITY,
            state=DEFAULT_STATE,
        ).first()

        if not default_address:
            default_address = Address(
                street=DEFAULT_STREET,
                city=DEFAULT_CITY,
                state=DEFAULT_STATE,
                zip_code="92101",
                country="USA",
                apt="Suite 103",
                is_default=True,
            )
            database.session.add(default_address)
            database.session.flush()

        existing = User.query.filter(User.email == admin_email).first()
        if existing:
            logger.info("Production admin already exists: %s", admin_email)
            return True

        password_service = PasswordService()
        admin_user = User(
            first_name=os.getenv("ADMIN_FIRST_NAME", "Admin"),
            last_name=os.getenv("ADMIN_LAST_NAME", "User"),
            email=admin_email,
            password_hash=password_service.hash_password(admin_password),
            status=UserStatus.ACTIVE,
            email_verified=True,
            role_id=admin_role.id,
            shipping_address_id=default_address.id,
            billing_address_id=default_address.id,
        )

        database.session.add(admin_user)
        database.session.commit()
        logger.info("Production admin created: %s", admin_email)
        return True
    except Exception:
        database.session.rollback()
        logger.exception("Failed to create production admin user")
        return False
