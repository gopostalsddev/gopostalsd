import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restx import Api
from server.services import FileStorage
from server.thirdparty import SinaliteAdapter as Sinalite
from dotenv import load_dotenv
from server.logging_config import configure_logging

# Configure third party libraries
database = SQLAlchemy()
migrate = Migrate()
sinalite = Sinalite()           # Implemented in house
filestorage = FileStorage()     # Implemented in house

# Configure Swagger UI documentation
swagger = Api(
    title="Go Postal SD API",
    version="1.0",
    description="API documentation for Go Postal SD",
    doc="/",
    validate=True
)

# Load .env file FIRST before checking environment
# This ensures environment variables from .env are available
load_dotenv()

# Check the current environment, default to 'development'
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

# Configure the logger
configure_logging(ENVIRONMENT)


def normalize_database_url(url):
    """Render provides postgres:// URLs; SQLAlchemy expects postgresql://."""
    if url and url.startswith('postgres://'):
        return url.replace('postgres://', 'postgresql://', 1)
    return url


def get_database_url():
    return normalize_database_url(os.getenv('DATABASE_URL'))


class Config:
    # Disable SQLAlchemy event system to improve performance
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    # Database connection string for development environment
    # Uses PostgreSQL from DATABASE_URL environment variable
    SQLALCHEMY_DATABASE_URI = get_database_url()

    # Sinalite integration information
    SINALITE_BASE_URL =  os.getenv('SINALITE_BASE_URL_DEV', 'https://api.sinaliteuppy.com') 
    SINALITE_CLIENT_ID = os.getenv('SINALITE_CLIENT_ID')
    SINALITE_CLIENT_SECRET = os.getenv('SINALITE_CLIENT_SECRET')

    if not SINALITE_CLIENT_ID or not SINALITE_CLIENT_SECRET:
        raise ValueError("SINALITE_CLIENT_ID and SINALITE_CLIENT_SECRET must be set in developement!")

class ProductionConfig(Config):
    # Database connection string for production environment
    # Format: postgresql://username:password@host:port/database_name
    SQLALCHEMY_DATABASE_URI = get_database_url()

    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError(
            "DATABASE_URL must be set in production. "
            "On Render: link your PostgreSQL instance or add DATABASE_URL in Environment."
        )

    # Sinalite integration information
    SINALITE_BASE_URL = os.getenv('SINALITE_BASE_URL')
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