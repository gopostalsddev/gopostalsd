#!/usr/bin/env python3
"""
Database setup script for gopostalsd backend.
This script handles database migrations and ensures the unclassified product type exists.
"""
import sys
from pathlib import Path

# Add the parent directory to the Python path to access server module
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

def setup_database():
    """Set up the database with migrations and initial data"""
    try:
        print("🚀 Setting up database for gopostalsd backend...")
        print("=" * 60)
        
        # Create Flask app
        print("📱 Initializing Flask application...")
        from server import create_server
        app = create_server()
        
        with app.app_context():
            print("📊 Running database migrations...")
            
            # Run migrations using Flask-Migrate
            from flask_migrate import upgrade
            upgrade()
            print("✅ Migrations completed successfully!")
            
            # Ensure the unclassified type exists
            print("🔧 Ensuring unclassified product type exists...")
            from server.startup import ensure_database_structures
            init_success = ensure_database_structures()
            
            if init_success:
                print("✅ Database initialization completed successfully!")
            else:
                print("⚠️ Database initialization completed with warnings")
            
            # Verify the setup
            print("🔍 Verifying database setup...")
            from server.startup import verify_database_health, check_database_tables_exist
            
            db_healthy = verify_database_health()
            tables_exist = check_database_tables_exist()
            
            if db_healthy and tables_exist:
                print("✅ Database setup verification passed!")
            else:
                print("❌ Database setup verification failed!")
                return False
            
            print("\n" + "=" * 60)
            print("🎉 Database setup completed successfully!")
            print("=" * 60)
            print("📋 Unclassified product type (ID 0) is now available")
            print("🔒 All products will default to this type if not classified")
            print("🚫 The unclassified type is protected from deletion/modification")
            print("💡 You can now use the admin interface to classify products")
            print("=" * 60)
            
            return True
            
    except Exception as e:
        print(f"❌ Error during database setup: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = setup_database()
    sys.exit(0 if success else 1)