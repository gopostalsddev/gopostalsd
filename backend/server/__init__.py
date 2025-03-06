# Import required Flask extensions and modules
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restx import Api
from flask_cors import CORS
from server.config import DevelopmentConfig, TestingConfig, ProductionConfig

# Initialize Flask extensions
database = SQLAlchemy()
migrate = Migrate()

# Configure Swagger UI documentation
swagger = Api(
    title = "Go Postal API",
    version = "1.0",
    description = "API documentation for Go Postal",
    doc = "/docs"
)

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

    # Initialize database and migration support
    database.init_app(server)
    migrate.init_app(server, database)

    # Register API routes
    #from server.routes import register_routes
    #register_routes(server)

    return server