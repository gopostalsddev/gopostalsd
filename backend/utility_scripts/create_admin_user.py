#!/usr/bin/env python3
"""
Script to create an admin user for testing admin functionality.
This script creates a user with the 'Admin' role and sets up the necessary permissions.
"""

import os
import sys
from pathlib import Path

# Add the server directory to the Python path
server_dir = Path(__file__).parent / "server"
sys.path.insert(0, str(server_dir))

from flask import Flask
from server import create_server
from server.config import database as db
from server.models.auth import User, Role, UserStatus, Address
from server.services.password_service import PasswordService
from server.services.role_service import RoleService

def create_admin_user():
    """Create an admin user for testing."""
    print("🔧 Creating admin user for testing...")
    print("=" * 60)
    
    try:
        # Create Flask app
        print("📱 Initializing Flask application...")
        app = create_server()
        
        with app.app_context():
            # Initialize services
            password_service = PasswordService()
            role_service = RoleService()
            
            # Ensure roles are initialized
            print("🔒 Ensuring roles are initialized...")
            role_service._initialize_default_roles()
            db.session.commit()
            
            # Get admin role
            admin_role = Role.query.filter_by(name='Admin').first()
            if not admin_role:
                print("❌ Admin role not found! Please run database setup first.")
                return False
            
            print(f"✅ Found admin role: {admin_role.name}")
            
            # Check if admin user already exists
            admin_email = "admin@gopostalsd.com"
            existing_admin = User.query.filter_by(email=admin_email).first()
            if existing_admin:
                print(f"⚠️ Admin user already exists: {admin_email}")
                print(f"   Role: {existing_admin.role.name}")
                print(f"   Status: {existing_admin.status.value}")
                print(f"   Email Verified: {existing_admin.email_verified}")
                
                # Ask if user wants to update the existing admin
                response = input("\nDo you want to update the existing admin user? (y/N): ").strip().lower()
                if response == 'y':
                    return update_existing_admin(existing_admin, password_service)
                else:
                    print("✅ Using existing admin user")
                    return True
            
            # Create default address for admin
            print("📍 Creating default address...")
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
            db.session.flush()  # Get the ID
            
            # Create admin user
            print("👤 Creating admin user...")
            admin_password = "Admin123!"  # You can change this
            password_hash = password_service.hash_password(admin_password)
            
            admin_user = User(
                first_name="Admin",
                last_name="User",
                email=admin_email,
                password_hash=password_hash,
                status=UserStatus.ACTIVE,
                email_verified=True,
                email_verified_at=db.func.now(),
                role_id=admin_role.id,
                shipping_address_id=default_address.id,
                billing_address_id=default_address.id
            )
            
            db.session.add(admin_user)
            db.session.commit()
            
            print("✅ Admin user created successfully!")
            print("=" * 60)
            print("📋 Admin User Details:")
            print(f"   Email: {admin_email}")
            print(f"   Password: {admin_password}")
            print(f"   Role: {admin_role.name}")
            print(f"   Status: {admin_user.status.value}")
            print(f"   Email Verified: {admin_user.email_verified}")
            print("=" * 60)
            print("🔐 Admin Permissions:")
            for permission in admin_role.permissions:
                print(f"   - {permission}")
            print("=" * 60)
            print("💡 You can now use these credentials to test admin functionality!")
            print("⚠️  Remember to change the password in production!")
            
            return True
            
    except Exception as e:
        print(f"❌ Error creating admin user: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def update_existing_admin(admin_user, password_service):
    """Update an existing admin user."""
    try:
        print("🔄 Updating existing admin user...")
        
        # Update password
        new_password = "Admin123!"  # You can change this
        admin_user.password_hash = password_service.hash_password(new_password)
        
        # Ensure user is active and verified
        admin_user.status = UserStatus.ACTIVE
        admin_user.email_verified = True
        
        # Ensure admin role
        admin_role = Role.query.filter_by(name='Admin').first()
        if admin_role:
            admin_user.role_id = admin_role.id
        
        db.session.commit()
        
        print("✅ Admin user updated successfully!")
        print("=" * 60)
        print("📋 Updated Admin User Details:")
        print(f"   Email: {admin_user.email}")
        print(f"   Password: {new_password}")
        print(f"   Role: {admin_user.role.name}")
        print(f"   Status: {admin_user.status.value}")
        print(f"   Email Verified: {admin_user.email_verified}")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating admin user: {str(e)}")
        return False

def main():
    """Main function."""
    print("🚀 Go Postal SD - Admin User Creation Script")
    print("=" * 60)
    
    success = create_admin_user()
    
    if success:
        print("\n🎉 Admin user setup completed successfully!")
        print("=" * 60)
        print("📝 Next Steps:")
        print("1. Use the admin credentials to log in")
        print("2. Test admin functionality in your application")
        print("3. Change the password for security")
        print("4. Consider creating additional admin users if needed")
        print("=" * 60)
        return 0
    else:
        print("\n❌ Admin user setup failed!")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
