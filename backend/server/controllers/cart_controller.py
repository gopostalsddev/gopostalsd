"""
Cart Controller for Go Postal SD Application

This module contains the business logic for cart-related operations.
It follows the same pattern as other controllers for clean separation of concerns.
"""

from server.controllers import Result
import logging

logger = logging.getLogger(__name__)


class CartController:
    """
    Controller for handling cart-related operations.
    Implements the Controller pattern for clean separation of concerns.
    """
    
    @staticmethod
    def get_cart_totals(cart_id: int) -> Result:
        """
        Get cart totals including subtotal, tax, and total.
        
        Args:
            cart_id: Cart ID
            
        Returns:
            Result containing cart totals
        """
        result = Result()
        
        try:
            # Get cart service from app context
            from flask import current_app
            cart_service = current_app.extensions.get('cart_service')
            
            if not cart_service:
                result.status = False
                result.error = "Cart service not available"
                return result
            
            totals = cart_service.get_cart_total(cart_id)
            
            result.data = totals
            
        except Exception:
            logger.error("Error getting cart totals", exc_info=True)
            result.status = False
            result.error = "Failed to get cart totals"
            
        return result
    
    @staticmethod
    def get_or_create_cart(session_id: str, user_id: int = None, store_code: int = 6) -> Result:
        """
        Get existing cart or create a new one.
        
        Args:
            session_id: Session ID for anonymous users
            user_id: User ID for logged-in users (optional)
            store_code: Store code (6 for Canada, 9 for US)
            
        Returns:
            Result containing cart information
        """
        result = Result()
        
        try:
            # Get cart service from app context
            from flask import current_app
            cart_service = current_app.extensions.get('cart_service')
            
            if not cart_service:
                result.status = False
                result.error = "Cart service not available"
                return result
            
            cart = cart_service.get_or_create_cart(session_id, user_id, store_code)
            
            result.data = {
                'cart_id': cart.id,
                'session_id': cart.session_id,
                'user_id': cart.user_id,
                'store_code': cart.store_code,
                'created_at': cart.created_at.isoformat() if cart.created_at else None,
                'updated_at': cart.updated_at.isoformat() if cart.updated_at else None
            }
            
        except Exception:
            logger.error("Error getting or creating cart", exc_info=True)
            result.status = False
            result.error = "Failed to get or create cart"
            
        return result
    
    @staticmethod
    def add_item_to_cart(cart_id: int, product_id: int, product_name: str,
                        product_sku: str, selected_options: list, quantity: int = 1) -> Result:
        """
        Add an item to the cart.
        
        Args:
            cart_id: Cart ID
            product_id: Product ID
            product_name: Product name
            product_sku: Product SKU
            selected_options: List of selected option IDs
            quantity: Quantity to add
            
        Returns:
            Result containing cart item information
        """
        result = Result()
        
        try:
            # Get cart service from app context
            from flask import current_app
            cart_service = current_app.extensions.get('cart_service')
            
            if not cart_service:
                result.status = False
                result.error = "Cart service not available"
                return result
            
            cart_item = cart_service.add_item_to_cart(
                cart_id, product_id, product_name, product_sku, selected_options, quantity
            )
            
            result.data = {
                'cart_item_id': cart_item.id,
                'cart_id': cart_item.cart_id,
                'product_id': cart_item.product_id,
                'product_name': cart_item.product_name,
                'product_sku': cart_item.product_sku,
                'selected_options': cart_item.selected_options,
                'quantity': cart_item.quantity,
                'created_at': cart_item.created_at.isoformat() if cart_item.created_at else None,
                'updated_at': cart_item.updated_at.isoformat() if cart_item.updated_at else None
            }
            
        except Exception:
            logger.error("Error adding item to cart", exc_info=True)
            result.status = False
            result.error = "Failed to add item to cart"
            
        return result
