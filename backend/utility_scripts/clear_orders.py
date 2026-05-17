"""
Clear all orders and related data from the database.
Use this script to clean up test data.

This will delete:
- Order items
- Payments
- Orders
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
from server.models.order import Order, OrderItem, Payment

def clear_orders():
    """Clear all orders, order items, and payments."""
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    db.init_app(app)
    
    with app.app_context():
        try:
            # Count items before deletion
            order_count = Order.query.count()
            order_item_count = OrderItem.query.count()
            payment_count = Payment.query.count()
            
            print(f"Found {order_count} orders, {order_item_count} order items, and {payment_count} payments")
            
            if order_count == 0 and order_item_count == 0 and payment_count == 0:
                print("No orders, items, or payments to delete")
                return
            
            # Delete in correct order (respecting foreign key constraints)
            # 1. Delete order items first (references orders)
            OrderItem.query.delete()
            print("✓ Deleted all order items")
            
            # 2. Delete payments (references orders)
            Payment.query.delete()
            print("✓ Deleted all payments")
            
            # 3. Delete orders last
            Order.query.delete()
            print("✓ Deleted all orders")
            
            # Commit the changes
            db.session.commit()
            
            print("\n✓ Successfully cleared all orders, order items, and payments")
            
        except Exception as e:
            print(f"Error clearing orders: {str(e)}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    clear_orders()

