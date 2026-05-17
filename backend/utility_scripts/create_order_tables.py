"""
Database Migration Script for Order Management Models

This script creates the necessary tables for order management functionality.
Run this script to add the order, order_item, payment, and refund tables to the database.
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from server.config import DevelopmentConfig
from server.models.order import Order, OrderItem, Payment, Refund

def create_order_tables():
    """Create order management tables in the database."""
    
    # Get database URL from config
    config = DevelopmentConfig()
    database_url = config.SQLALCHEMY_DATABASE_URI
    
    print(f"Connecting to database: {database_url}")
    
    # Create engine and session
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Create tables
        print("Creating order management tables...")
        
        # Create Order table
        Order.__table__.create(engine, checkfirst=True)
        print("✓ Created 'orders' table")
        
        # Create OrderItem table
        OrderItem.__table__.create(engine, checkfirst=True)
        print("✓ Created 'order_items' table")
        
        # Create Payment table
        Payment.__table__.create(engine, checkfirst=True)
        print("✓ Created 'payments' table")
        
        # Create Refund table
        Refund.__table__.create(engine, checkfirst=True)
        print("✓ Created 'refunds' table")
        
        print("\n✅ All order management tables created successfully!")
        
        # Verify tables exist
        print("\nVerifying tables...")
        result = session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND (table_name LIKE '%order%' OR table_name LIKE '%payment%' OR table_name LIKE '%refund%')"))
        tables = result.fetchall()
        
        for table in tables:
            print(f"✓ Table '{table[0]}' exists")
            
    except Exception as e:
        print(f"❌ Error creating tables: {str(e)}")
        session.rollback()
        raise
    finally:
        session.close()

def drop_order_tables():
    """Drop order management tables from the database."""
    
    # Get database URL from config
    config = DevelopmentConfig()
    database_url = config.SQLALCHEMY_DATABASE_URI
    
    print(f"Connecting to database: {database_url}")
    
    # Create engine and session
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        print("Dropping order management tables...")
        
        # Drop tables in reverse order (due to foreign key constraints)
        Refund.__table__.drop(engine, checkfirst=True)
        print("✓ Dropped 'refunds' table")
        
        Payment.__table__.drop(engine, checkfirst=True)
        print("✓ Dropped 'payments' table")
        
        OrderItem.__table__.drop(engine, checkfirst=True)
        print("✓ Dropped 'order_items' table")
        
        Order.__table__.drop(engine, checkfirst=True)
        print("✓ Dropped 'orders' table")
        
        print("\n✅ All order management tables dropped successfully!")
        
    except Exception as e:
        print(f"❌ Error dropping tables: {str(e)}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Order Management Database Migration")
    parser.add_argument("action", choices=["create", "drop"], help="Action to perform")
    
    args = parser.parse_args()
    
    if args.action == "create":
        create_order_tables()
    elif args.action == "drop":
        drop_order_tables()
