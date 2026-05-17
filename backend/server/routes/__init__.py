from flask import Flask
from server.config import swagger
from server.routes.print_product_routes import api as print_products_namespace
from server.routes.pricing_routes import api as pricing_namespace
from server.routes.cart_routes import api as cart_namespace
from server.routes.auth_routes import api as auth_namespace
from server.routes.contact_routes import api as contact_namespace
from server.routes.payment_routes import api as payment_namespace
from server.routes.order_routes import api as order_namespace
from server.routes.misc_routes import api as misc_blueprint


def register_routes(server: Flask):
    """
    Registers all API routes with the Flask application.

    Args:
        server (Flask): The Flask application instance.
    """
    # Register API namespaces
    swagger.add_namespace(print_products_namespace, path="/api/print")
    swagger.add_namespace(pricing_namespace, path="/api/pricing")
    swagger.add_namespace(cart_namespace, path="/api/cart")
    swagger.add_namespace(auth_namespace, path="/api/auth")
    swagger.add_namespace(contact_namespace, path="/api/contact")
    swagger.add_namespace(payment_namespace, path="/api/payments")
    swagger.add_namespace(order_namespace, path="/api/orders")
    
    # Register blueprints
    server.register_blueprint(misc_blueprint)

