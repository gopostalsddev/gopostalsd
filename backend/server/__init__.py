# Import required Flask extensions and modules
from flask import Flask
from flask_cors import CORS
from server.config import DevelopmentConfig, TestingConfig, ProductionConfig, validate_production_security_settings
from server.config import database, migrate, sinalite, swagger, filestorage
from server.models import * # So that they can be detected by migrations
import logging
import os

logger = logging.getLogger(__name__)
def create_server(config="development"):
    """
    Factory function to create and configure the Flask application.
    
    Args:
        config (str): Configuration environment to use ('development', 'testing', or 'production')
    
    Returns:
        Flask: Configured Flask application instance
    """
    # Create Flask application instance
    server = Flask(__name__)
    
    # Configure CORS with allowed origins
    frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
    render_frontend_url = os.getenv('RENDER_FRONTEND_URL')
    render_external_url = os.getenv('RENDER_EXTERNAL_URL')

    env_origins = [origin for origin in [frontend_url, render_frontend_url, render_external_url] if origin]
    if config == "production":
        cors_origins = list(dict.fromkeys(env_origins))
    else:
        cors_origins = [
            'http://localhost:5173',
            'http://localhost:3000',
            'http://localhost:8080',
            'https://localhost:5173',
        ]
        for origin in env_origins:
            if origin not in cors_origins:
                cors_origins.append(origin)

    if not cors_origins:
        raise ValueError("No CORS origins configured for this environment")
    
    # Extract base domain for Codespaces (e.g., curly-spoon-jj57pprxw5q93qjwq)
    if config != "production" and frontend_url and 'github.dev' in frontend_url:
        # Extract the subdomain part
        import re
        match = re.search(r'https?://([^.]+)\.app\.github\.dev', frontend_url)
        if match:
            subdomain = match.group(1)
            # Add both port 5173 (frontend) and 5000 (backend) with this subdomain
            cors_origins.append(f'https://{subdomain}-5173.app.github.dev')
            cors_origins.append(f'https://{subdomain}-5000.app.github.dev')
    
    cors_config = {
        'origins': cors_origins,
        'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
        'allow_headers': ['Content-Type', 'Authorization', 'X-CSRF-Token'],
        'supports_credentials': True,
        'max_age': 3600,
        'expose_headers': ['Content-Type', 'Authorization']
    }
    CORS(server, resources={r"/api/*": cors_config})

    # Enforce CSRF validation for authenticated state-changing requests.
    from server.middleware.auth_middleware import enforce_csrf_protection
    server.before_request(enforce_csrf_protection)
    
    # Add startup timestamp for health checks
    from datetime import datetime
    server.config['START_TIME'] = datetime.utcnow().isoformat()

    # Load configuration based on environment
    if config == "testing":
        server.config.from_object(TestingConfig)
    elif config == "production":
        validate_production_security_settings()
        server.config.from_object(ProductionConfig)
    else:  # Default to development configuration
        server.config.from_object(DevelopmentConfig)

    # Log the loaded environment and Sinalite URL
    logger.info(f"Loaded Environment: {config}")
    logger.info(f"Sinalite: {server.config['SINALITE_BASE_URL']}")

    # Initialize database support
    database.init_app(server)

    if config == "production":
        with server.app_context():
            from server.startup_admin import ensure_production_admin
            ensure_production_admin(server)

    # Initialize database support
    migrate.init_app(server, database)

    # Initialize sinalite api support
    sinalite.init_app(server)

    # Initialize swagger documentation
    swagger.init_app(server)

    # Initialize file storage for image storing
    filestorage.init_app(server)
    logger.info(f"File Storage: {filestorage.current_backend}")
    
    # Initialize services using factory pattern
    from server.factories.main_factory import MainFactory
    from server.thirdparty.sinalite import SinaliteAdapter
    
    # Create main factory and services
    main_factory = MainFactory()
    sinalite_adapter = SinaliteAdapter(server)
    pricing_service = main_factory.get_pricing_service(sinalite_adapter)
    cart_service = main_factory.get_cart_service(pricing_service, sinalite_adapter)
    email_service = main_factory.get_email_service()
    email_service.init_app(server)  # Initialize email service with Flask app
    password_service = main_factory.get_password_service()
    role_service = main_factory.get_role_service()
    auth_service = main_factory.get_auth_service()
    
    # Store in Flask app context for use in API routes
    server.extensions['main_factory'] = main_factory
    server.extensions['sinalite_adapter'] = sinalite_adapter
    server.extensions['pricing_service'] = pricing_service
    server.extensions['cart_service'] = cart_service
    server.extensions['email_service'] = email_service
    server.extensions['password_service'] = password_service
    server.extensions['role_service'] = role_service
    server.extensions['auth_service'] = auth_service
    
    # Register API routes
    from server.routes import register_routes
    register_routes(server)

    # Initialize centralized error handling and severity categorization.
    try:
        from server.exceptions.error_handler import ErrorHandler
        ErrorHandler(server)
    except ImportError:
        logger.warning("Advanced error handler dependencies are unavailable; continuing with default handlers")

    if config == "production":
        with server.app_context():
            from server.startup import ensure_database_structures
            ensure_database_structures()

    return server