# Import required Flask extensions and modules
from flask import Flask
from flask_cors import CORS
from server.config import DevelopmentConfig, TestingConfig, ProductionConfig
from server.config import database, migrate, sinalite, swagger, filestorage
from server.models import * # So that they can be detected by migrations
import logging

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
    # Enable Cross-Origin Resource Sharing (CORS)
    CORS(server)
    
    # Add startup timestamp for health checks
    from datetime import datetime
    server.config['START_TIME'] = datetime.utcnow().isoformat()

    # Load configuration based on environment
    if config == "testing":
        server.config.from_object(TestingConfig)
    elif config == "production":
        server.config.from_object(ProductionConfig)
    else:  # Default to development configuration
        server.config.from_object(DevelopmentConfig)

    # Log the loaded environment and Sinalite URL
    logger.info(f"Loaded Environment: {config}")
    logger.info(f"Sinalite: {server.config['SINALITE_BASE_URL']}")

    # Initialize database support
    database.init_app(server)

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

    return server