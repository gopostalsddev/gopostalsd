"""
Simple script to verify order tables exist in the database.
"""

from server.config import DevelopmentConfig
from sqlalchemy import create_engine, text

def verify_tables():
    config = DevelopmentConfig()
    engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND (table_name LIKE '%order%' OR table_name LIKE '%payment%' OR table_name LIKE '%refund%')
                ORDER BY table_name
            """))
            tables = result.fetchall()
            
            print("Order-related tables:")
            for table in tables:
                print(f"✓ {table[0]}")
                
            if not tables:
                print("No order-related tables found.")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_tables()
