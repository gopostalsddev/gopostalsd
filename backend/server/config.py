import os

class Config:
    # Disable SQLAlchemy event system to improve performance
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    # Database connection string for development environment
    # Defaults to SQLite if DATABASE_URL environment variable is not set
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///gopostal.db')

class ProductionConfig(Config):
    # Database connection string for production environment
    # Defaults to PostgreSQL if DATABASE_URL environment variable is not set
    # Format: postgresql://username:password@host:port/database_name
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/gopostal_db')

class TestingConfig(Config):
    # In-memory database for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    TESTING = True 