from flask import Flask
from server.config import swagger
from server.routes.print_product_routes import api as print_products_namespace
from server.routes.misc_routes import api as misc_blueprint


def register_routes(server: Flask):
    """
    Registers all API routes with the Flask application.

    Args:
        server (Flask): The Flask application instance.
    """
    # Register API namespace
    swagger.add_namespace(print_products_namespace, path="/api/print")
    server.register_blueprint(misc_blueprint)

