"""
Clear all carts and cart items from the database.
Use this script to clean up test data.
"""

import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Import Flask app initialization
from flask import Flask
from server.config import database as db
from server.config import DevelopmentConfig
from server.models.pricing import Cart, CartItem

def clear_carts():
    """Clear all carts and cart items."""
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    db.init_app(app)
    
    with app.app_context():
        try:
            # Count items before deletion
            cart_count = Cart.query.count()
            cart_item_count = CartItem.query.count()
            
            print(f"Found {cart_count} carts and {cart_item_count} cart items")
            
            if cart_count == 0 and cart_item_count == 0:
                print("No carts or items to delete")
                return
            
            # Delete all cart items first (foreign key constraint)
            CartItem.query.delete()
            print("✓ Deleted all cart items")
            
            # Delete all carts
            Cart.query.delete()
            print("✓ Deleted all carts")
            
            # Commit the changes
            db.session.commit()
            
            print("\n✓ Successfully cleared all carts and cart items")
            
        except Exception as e:
            print(f"Error clearing carts: {str(e)}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    clear_carts()

