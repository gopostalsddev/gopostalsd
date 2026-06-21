#!/usr/bin/env python3
"""
Simple script to run Flask database migrations
"""
import os
import sys
from pathlib import Path

# Add backend root to the Python path so `server` package can be imported.
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from flask import Flask
from flask_migrate import Migrate
from server.config import database as db
from server import create_server

def run_migrations():
    """Run database migrations"""
    try:
        # Create Flask app
        app = create_server()
        
        with app.app_context():
            # Initialize migrations
            migrate = Migrate(app, db)
            
            print("Running database migrations...")
            
            # Import and run migrations
            from flask_migrate import upgrade
            upgrade()
            
            print("✅ Migrations completed successfully!")
            
    except Exception as e:
        print(f"❌ Error running migrations: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = run_migrations()
    sys.exit(0 if success else 1) 