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

    
    # Register API routes
    from server.routes import register_routes
    register_routes(server)

    return server