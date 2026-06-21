import logging
import os
from datetime import datetime

from flask import Flask
from sqlalchemy import or_

from server.config import database
from server.models.auth import Address, Role, User, UserStatus
from server.services.password_service import PasswordService

logger = logging.getLogger(__name__)

DEFAULT_STREET = "1501 India St Suite 103"
DEFAULT_CITY = "San Diego"
DEFAULT_STATE = "CA"


def ensure_production_admin(app: Flask) -> None:
    """Create John Doe as Admin in production when ADMIN_EMAIL and ADMIN_PASSWORD are set."""
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")

    if not admin_email or not admin_password:
        return

    try:
        admin_role = Role.query.filter_by(name="Admin").first()
        if not admin_role:
            logger.warning(
                "Admin role not found; skipping production admin bootstrap. "
                "Run database migrations first."
            )
            return

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

        existing = User.query.filter(
            or_(
                User.email == admin_email,
                User.legacy_email_address == admin_email,
            )
        ).first()
        if existing:
            logger.info("Production admin already exists: %s", admin_email)
            return

        password_service = PasswordService()
        admin_user = User(
            first_name="John",
            last_name="Doe",
            email=admin_email,
            legacy_email_address=admin_email,
            legacy_creation_date=datetime.utcnow(),
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
    except Exception:
        database.session.rollback()
        logger.exception("Failed to create production admin user")
