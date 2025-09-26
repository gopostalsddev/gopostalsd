"""
Pricing Routes for Go Postal SD Application

This module registers pricing-related routes with the Flask application.
It initializes the pricing controller and makes it available to the app context.
"""

from flask import Flask
from server.controllers.pricing_controller import pricing_ns
import logging

logger = logging.getLogger(__name__)


def register_pricing_routes(app: Flask) -> None:
    """
    Register pricing routes with the Flask application.
    
    Args:
        app: Flask application instance
    """
    try:
        # Verify that pricing controller is already available in app extensions
        pricing_controller = app.extensions.get('pricing_controller')
        
        if not pricing_controller:
            logger.error("Pricing controller not found in app extensions")
            return
        
        # Register the namespace with the API
        from server.config import swagger
        swagger.add_namespace(pricing_ns, path='/api/pricing')
        
        logger.info("Pricing routes registered successfully")
        
    except Exception as e:
        logger.error(f"Error registering pricing routes: {str(e)}")
        raise
