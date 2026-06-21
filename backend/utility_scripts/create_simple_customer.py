#!/usr/bin/env python3
"""
Create a RegisteredCustomer test user directly in the database.
"""

import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from server import create_server
from server.config import database as db
from server.models.auth import User, Role, UserStatus, Address
from server.services.password_service import PasswordService

CUSTOMER_EMAIL = "john.doe@gopostalsd.com"
CUSTOMER_PASSWORD = "Customer123!"


def create_simple_customer():
    """Create John Doe as a RegisteredCustomer."""
    app = create_server()

    with app.app_context():
        customer_role = Role.query.filter_by(name="RegisteredCustomer").first()
        if not customer_role:
            print("RegisteredCustomer role not found. Run database setup first.")
            return False

        default_address = Address.query.filter_by(
            street="1501 India St Suite 103",
            city="San Diego",
            state="CA",
        ).first()

        if not default_address:
            default_address = Address(
                street="1501 India St Suite 103",
                city="San Diego",
                state="CA",
                zip_code="92101",
                country="USA",
                apt="Suite 103",
                is_default=True,
            )
            db.session.add(default_address)
            db.session.flush()

        existing = User.query.filter_by(email=CUSTOMER_EMAIL).first()
        if existing:
            print(f"Customer user already exists: {CUSTOMER_EMAIL}")
            return True

        password_service = PasswordService()
        customer = User(
            first_name="John",
            last_name="Doe",
            email=CUSTOMER_EMAIL,
            password_hash=password_service.hash_password(CUSTOMER_PASSWORD),
            status=UserStatus.ACTIVE,
            email_verified=True,
            role_id=customer_role.id,
            shipping_address_id=default_address.id,
            billing_address_id=default_address.id,
        )

        db.session.add(customer)
        db.session.commit()

        print("Customer user created!")
        print(f"Name: John Doe")
        print(f"Email: {CUSTOMER_EMAIL}")
        print(f"Password: {CUSTOMER_PASSWORD}")
        print(f"Role: RegisteredCustomer")
        return True


if __name__ == "__main__":
    create_simple_customer()
