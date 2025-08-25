#!/usr/bin/env python3
"""
Script to set up the unclassified product type system
Creates the wildcard product type (ID 0) and updates database schema
"""
import os
import sys
from pathlib import Path

# Add the server directory to the Python path
server_dir = Path(__file__).parent.parent / "server"
sys.path.insert(0, str(server_dir))

from flask import Flask
from flask_migrate import upgrade
from server import create_server
from server.controllers.print_product_controller import PrintProductController

def main():
    """Main function to run the migration and setup"""
    print("🚀 Setting up unclassified product type system...")
    print("=" * 60)
    
    try:
        # Create Flask app
        print("📱 Initializing Flask application...")
        app = create_server()
        
        with app.app_context():
            print("📊 Running database migration...")
            
            # Run the migration
            upgrade()
            print("✅ Migration completed successfully!")
            
            # Ensure the unclassified type exists
            print("🔧 Ensuring unclassified product type exists...")
            result = PrintProductController.ensure_unclassified_type_exists()
            
            if result.status:
                print(f"✅ {result.data['message']}")
            else:
                print(f"❌ Error: {result.error}")
                return 1
            
            print("\n" + "=" * 60)
            print("🎉 Setup completed successfully!")
            print("=" * 60)
            print("📋 Unclassified product type (ID 0) is now available")
            print("🔒 All products will default to this type if not classified")
            print("🚫 The unclassified type is protected from deletion/modification")
            print("💡 You can now use the admin interface to classify products")
            print("=" * 60)
            
            return 0
            
    except Exception as e:
        print(f"❌ Error during setup: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 