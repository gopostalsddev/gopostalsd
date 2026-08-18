import logging
import os

from flask import Flask

from server.config import database
from server.models.auth import Address, Role, User, UserStatus
from server.services.password_service import PasswordService

logger = logging.getLogger(__name__)

def ensure_production_admin(app: Flask) -> bool:
    """Create the configured Admin when explicitly invoked after migrations."""
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")

    if not admin_email or not admin_password:
        return False

    address = {
        "street": os.getenv("ADMIN_STREET", "").strip(),
        "city": os.getenv("ADMIN_CITY", "").strip(),
        "state": os.getenv("ADMIN_STATE", "").strip(),
        "zip_code": os.getenv("ADMIN_ZIP_CODE", "").strip(),
        "country": os.getenv("ADMIN_COUNTRY", "USA").strip(),
        "apt": os.getenv("ADMIN_APT", "").strip() or None,
    }
    missing = [key for key in ("street", "city", "state", "zip_code") if not address[key]]
    if missing:
        logger.error("Production admin address configuration is incomplete: %s", ", ".join(missing))
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
            street=address["street"],
            city=address["city"],
            state=address["state"],
        ).first()

        if not default_address:
            default_address = Address(
                **address,
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
