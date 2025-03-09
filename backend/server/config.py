import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from server.thirdparty import SinaliteAdapter as Sinalite
from dotenv import load_dotenv
from server.logging import configure_logging

# Configure third party libraries
database = SQLAlchemy()
migrate = Migrate()
sinalite = Sinalite() # Implemented in house

# Check the current environment, default to 'development'
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

# Configure the logger
configure_logging(ENVIRONMENT)

# Only load .env in development or testing
if ENVIRONMENT in ['development', 'testing']:
    load_dotenv()

class Config:
    # Disable SQLAlchemy event system to improve performance
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    # Database connection string for development environment
    # Defaults to SQLite if DATABASE_URL environment variable is not set
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///gopostalsd.db')

    # Sinalite integration information
    SINALITE_BASE_URL = 'https://api.sinaliteuppy.com'
    SINALITE_CLIENT_ID = os.getenv('SINALITE_CLIENT_ID')
    SINALITE_CLIENT_SECRET = os.getenv('SINALITE_CLIENT_SECRET')

    if not SINALITE_CLIENT_ID or not SINALITE_CLIENT_SECRET:
        raise ValueError("SINALITE_CLIENT_ID and SINALITE_CLIENT_SECRET must be set in developement!")

class ProductionConfig(Config):
    # Database connection string for production environment
    # Defaults to PostgreSQL if DATABASE_URL environment variable is not set
    # Format: postgresql://username:password@host:port/database_name
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/gopostalsd_db')

    # Sinalite integration information
    SINALITE_BASE_URL = 'https://liveapi.sinalite.com'
    SINALITE_CLIENT_ID = os.getenv('SINALITE_CLIENT_ID')
    SINALITE_CLIENT_SECRET = os.getenv('SINALITE_CLIENT_SECRET')

    if not SINALITE_CLIENT_ID or not SINALITE_CLIENT_SECRET:
        raise ValueError("SINALITE_CLIENT_ID and SINALITE_CLIENT_SECRET must be set in production!")

class TestingConfig(Config):
    # In-memory database for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    TESTING = True 

    # Sinalite integration information
    SINALITE_BASE_URL = 'https://api.sinaliteuppy.com'
    SINALITE_CLIENT_ID = os.getenv('SINALITE_CLIENT_ID')
    SINALITE_CLIENT_SECRET = os.getenv('SINALITE_CLIENT_SECRET')

    if not SINALITE_CLIENT_ID or not SINALITE_CLIENT_SECRET:
        raise ValueError("SINALITE_CLIENT_ID and SINALITE_CLIENT_SECRET must be set in  testing!")