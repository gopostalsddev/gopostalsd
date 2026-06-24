#!/usr/bin/env python3
"""
Simple script to create an admin user directly in the database.
This is a more direct approach if you prefer to handle it manually.
"""

import os
import sys
from pathlib import Path

# Add the server directory to the Python path
server_dir = Path(__file__).parent / "server"
sys.path.insert(0, str(server_dir))

from server import create_server
from server.config import database as db
from server.models.auth import User, Role, UserStatus, Address
from server.services.password_service import PasswordService

def create_simple_admin():
    """Create a simple admin user."""
    app = create_server()
    
    with app.app_context():
        # Get admin role
        admin_role = Role.query.filter_by(name='Admin').first()
        if not admin_role:
            print("❌ Admin role not found. Run database setup first.")
            return False
        
        # Create or get default address
        default_address = Address.query.filter_by(
            street="1501 India St Suite 103",
            city="San Diego",
            state="CA"
        ).first()
        
        if not default_address:
            default_address = Address(
                street="1501 India St Suite 103",
                city="San Diego", 
                state="CA",
                zip_code="92101",
                country="USA",
                apt="Suite 103",
                is_default=True
            )
            db.session.add(default_address)
            db.session.flush()
        
        # Check if admin exists
        admin_email = "admin@gopostalsd.com"
        admin_user = User.query.filter_by(email=admin_email).first()
        
        if admin_user:
            print(f"✅ Admin user already exists: {admin_email}")
            return True
        
        # Create admin user
        password_service = PasswordService()
        admin_user = User(
            first_name="Admin",
            last_name="User", 
            email=admin_email,
            password_hash=password_service.hash_password("Admin123!"),
            status=UserStatus.ACTIVE,
            email_verified=True,
            role_id=admin_role.id,
            shipping_address_id=default_address.id,
            billing_address_id=default_address.id
        )
        
        db.session.add(admin_user)
        db.session.commit()
        
        print("✅ Admin user created!")
        print(f"Email: {admin_email}")
        print("Password: Admin123!")
        return True

if __name__ == "__main__":
    create_simple_admin()
