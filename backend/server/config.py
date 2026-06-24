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

# Load .env file FIRST before checking environment
# This ensures environment variables from .env are available
load_dotenv()

# Check the current environment, default to 'development'
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

# Configure the logger
configure_logging(ENVIRONMENT)

# Configure Swagger UI documentation
_swagger_enabled = ENVIRONMENT != 'production' and os.getenv('ENABLE_SWAGGER_UI', 'true').lower() == 'true'
swagger = Api(
    title="Go Postal SD API",
    version="1.0",
    description="API documentation for Go Postal SD",
    doc="/docs" if _swagger_enabled else False,
    validate=True
)


def normalize_database_url(url):
    """Render provides postgres:// URLs; SQLAlchemy expects postgresql://."""
    if url and url.startswith('postgres://'):
        return url.replace('postgres://', 'postgresql://', 1)
    return url


def get_database_url():
    return normalize_database_url(os.getenv('DATABASE_URL'))


def validate_production_security_settings() -> None:
    """Raise if insecure production environment settings are detected."""
    if os.getenv('DEBUG', 'false').lower() == 'true':
        raise ValueError('DEBUG must be false in production')

    if os.getenv('SESSION_COOKIE_SECURE', 'true').lower() != 'true':
        raise ValueError('SESSION_COOKIE_SECURE must be true in production')

    secret_key = os.getenv('SECRET_KEY', '').strip()
    jwt_secret_key = os.getenv('JWT_SECRET_KEY', '').strip()
    if not secret_key or secret_key == 'your_flask_secret_key_here':
        raise ValueError('A strong SECRET_KEY must be set in production')

    # Keep production boot resilient when JWT_SECRET_KEY is accidentally omitted
    # in the hosting dashboard by falling back to a verified strong SECRET_KEY.
    if not jwt_secret_key or jwt_secret_key == 'your_jwt_secret_key_here':
        os.environ['JWT_SECRET_KEY'] = secret_key


class Config:
    # Disable SQLAlchemy event system to improve performance
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    PRICING_POLICY_VERSION = os.getenv('PRICING_POLICY_VERSION', 'retail-v1')
    PRICING_VENDOR_CURRENCY = os.getenv('PRICING_VENDOR_CURRENCY', 'CAD').upper()
    PRICING_DISPLAY_CURRENCY = os.getenv('PRICING_DISPLAY_CURRENCY', 'USD').upper()
    PRICING_CAD_TO_USD_RATE = float(os.getenv('PRICING_CAD_TO_USD_RATE', '0.74'))
    PRICING_EXCHANGE_BUFFER_PERCENT = float(os.getenv('PRICING_EXCHANGE_BUFFER_PERCENT', '5'))
    PRICING_MARKUP_PERCENT = float(os.getenv('PRICING_MARKUP_PERCENT', '30'))
    PRICING_FIXED_FEE_USD = float(os.getenv('PRICING_FIXED_FEE_USD', '0'))
    PRICING_MINIMUM_PROFIT_USD = float(os.getenv('PRICING_MINIMUM_PROFIT_USD', '0'))
    PRICING_ROUNDING_INCREMENT = os.getenv('PRICING_ROUNDING_INCREMENT', '0.05')
    CUSTOMIZATION_FILE_REVIEW_FEE_USD = float(os.getenv('CUSTOMIZATION_FILE_REVIEW_FEE_USD', '10'))
    CUSTOMIZATION_DESIGN_ASSIST_FEE_USD = float(os.getenv('CUSTOMIZATION_DESIGN_ASSIST_FEE_USD', '35'))

    # Security/auth settings
    PASSWORD_HASH_ITERATIONS = int(os.getenv('PASSWORD_HASH_ITERATIONS', '100000'))
    SESSION_EXPIRY_DAYS = int(os.getenv('SESSION_EXPIRY_DAYS', '7'))
    MAX_FAILED_LOGIN_ATTEMPTS = int(os.getenv('MAX_FAILED_LOGIN_ATTEMPTS', '5'))
    ACCOUNT_LOCKOUT_MINUTES = int(os.getenv('ACCOUNT_LOCKOUT_MINUTES', '30'))
    EMAIL_VERIFICATION_EXPIRY_HOURS = int(os.getenv('EMAIL_VERIFICATION_EXPIRY_HOURS', '24'))
    PASSWORD_RESET_EXPIRY_HOURS = int(os.getenv('PASSWORD_RESET_EXPIRY_HOURS', '1'))

    AUTH_RATE_LIMIT_ENABLED = os.getenv('AUTH_RATE_LIMIT_ENABLED', 'true').lower() == 'true'
    AUTH_RATE_LIMIT_STORE = os.getenv('AUTH_RATE_LIMIT_STORE', 'memory')
    RATE_LIMIT_REDIS_URL = os.getenv('RATE_LIMIT_REDIS_URL', '')
    AUTH_LOGIN_RATE_LIMIT_COUNT = int(os.getenv('AUTH_LOGIN_RATE_LIMIT_COUNT', '10'))
    AUTH_LOGIN_RATE_LIMIT_WINDOW_SECONDS = int(os.getenv('AUTH_LOGIN_RATE_LIMIT_WINDOW_SECONDS', '300'))
    AUTH_REGISTER_RATE_LIMIT_COUNT = int(os.getenv('AUTH_REGISTER_RATE_LIMIT_COUNT', '5'))
    AUTH_REGISTER_RATE_LIMIT_WINDOW_SECONDS = int(os.getenv('AUTH_REGISTER_RATE_LIMIT_WINDOW_SECONDS', '3600'))
    AUTH_PASSWORD_RESET_RATE_LIMIT_COUNT = int(os.getenv('AUTH_PASSWORD_RESET_RATE_LIMIT_COUNT', '5'))
    AUTH_PASSWORD_RESET_RATE_LIMIT_WINDOW_SECONDS = int(os.getenv('AUTH_PASSWORD_RESET_RATE_LIMIT_WINDOW_SECONDS', '3600'))
    CONTACT_RATE_LIMIT_COUNT = int(os.getenv('CONTACT_RATE_LIMIT_COUNT', '5'))
    CONTACT_RATE_LIMIT_WINDOW_SECONDS = int(os.getenv('CONTACT_RATE_LIMIT_WINDOW_SECONDS', '300'))

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

    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')

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

    AUTH_RATE_LIMIT_ENABLED = False
    AUTH_RATE_LIMIT_STORE = 'memory'

    if not SINALITE_CLIENT_ID or not SINALITE_CLIENT_SECRET:
        raise ValueError("SINALITE_CLIENT_ID and SINALITE_CLIENT_SECRET must be set in  testing!")