#!/usr/bin/env python3
"""
Create database migration for authentication system
"""

from server import create_server

def create_migration():
    """Create migration for authentication system"""
    print("🔧 Creating server...")
    app = create_server()
    
    print("✅ Server created successfully")
    
    print("\n📊 Creating migration...")
    with app.app_context():
        from server.config import database as db, migrate
        
        # Create a new migration
        print("Generating migration...")
        try:
            migrate.init()
            migrate.revision(message="Add authentication system tables and columns")
            print("✅ Migration created successfully")
        except Exception as e:
            print(f"❌ Error creating migration: {e}")
            
        # Show current migration status
        print("\nCurrent migration status:")
        try:
            from flask_migrate import current, history
            print(f"Current version: {current()}")
            print("Migration history:")
            for migration in history():
                print(f"  - {migration.revision}: {migration.doc}")
        except Exception as e:
            print(f"Error checking migration status: {e}")

if __name__ == '__main__':
    create_migration()
