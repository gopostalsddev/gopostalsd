"""
Pricing Controller for Go Postal SD Application

This module contains the business logic for pricing-related operations.
It follows the same pattern as print_product_controller.py.
"""

from server.controllers import Result
import logging

logger = logging.getLogger(__name__)


class PricingController:
    """
    Controller for handling pricing-related operations.
    Implements the Controller pattern for clean separation of concerns.
    """
    
    @staticmethod
    def get_product_options(product_id: int, store_code: int) -> Result:
        """
        Get available options for a product.
        
        Args:
            product_id: Sinalite product ID
            store_code: Store code (6 for Canada, 9 for US)
            
        Returns:
            Result containing grouped product options
        """
        result = Result()
        
        try:
            # Get pricing service from app context
            from flask import current_app
            pricing_service = current_app.extensions.get('pricing_service')
            
            if not pricing_service:
                result.status = False
                result.error = "Pricing service not available"
                return result
            
            options = pricing_service.get_product_options(product_id, store_code)
            
            result.data = {
                    'product_id': product_id,
                    'store_code': store_code,
                    'options': options
            }
            
        except Exception as e:
            logger.error(f"Error getting product options: {str(e)}")
            result.status = False
            result.error = "Failed to retrieve product options"
            result.details = str(e)
        
        return result
    
    @staticmethod
    def calculate_price(product_id: int, options: list, store_code: int) -> Result:
        """
        Calculate price for a product with selected options.
        
        Args:
            product_id: Sinalite product ID
            options: List of selected option IDs
            store_code: Store code (6 for Canada, 9 for US)
            
        Returns:
            Result containing pricing information
        """
        result = Result()
        
        try:
            # Get pricing service from app context
            from flask import current_app
            pricing_service = current_app.extensions.get('pricing_service')
            
            if not pricing_service:
                result.status = False
                result.error = "Pricing service not available"
                return result
            
            pricing = pricing_service.calculate_product_price(product_id, options, store_code)
            
            if not pricing:
                result.status = False
                result.error = "Failed to calculate price"
                return result
            
            result.data = pricing
            
        except Exception as e:
            logger.error(f"Error calculating price: {str(e)}")
            result.status = False
            result.error = "Failed to calculate price"
            result.details = str(e)
        
        return result
    
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
            
            totals = cart_service.get_cart_totals(cart_id)
            result.data = totals
            
        except Exception as e:
            logger.error(f"Error getting cart totals: {str(e)}")
            result.status = False
            result.error = "Failed to get cart totals"
            result.details = str(e)
        
        return result
    
    @staticmethod
    def get_shipping_estimates(items: list, shipping_info: dict) -> Result:
        """
        Get shipping estimates for cart items.
        
        Args:
            items: List of cart items
            shipping_info: Shipping destination information
            
        Returns:
            Result containing available shipping options
        """
        result = Result()
        
        try:
            logger.info(f"PricingController.get_shipping_estimates called with:")
            logger.info(f"items: {items}")
            logger.info(f"shipping_info: {shipping_info}")
            
            # Get pricing service from app context
            from flask import current_app
            pricing_service = current_app.extensions.get('pricing_service')
            
            if not pricing_service:
                result.status = False
                result.error = "Pricing service not available"
                return result
            
            estimates = pricing_service.get_shipping_estimates(items, shipping_info)
            
            logger.info(f"PricingController received estimates: {estimates}")
            
            result.data = {
                'shipping_options': estimates,
                'count': len(estimates)
            }
            
        except Exception as e:
            logger.error(f"Error getting shipping estimates: {str(e)}")
            result.status = False
            result.error = "Failed to get shipping estimates"
            result.details = str(e)
        
        return result
    
    @staticmethod
    def get_or_create_cart(session_id: str, user_id: int = None, store_code: int = 6) -> Result:
        """
        Get or create a cart.
        
        Args:
            session_id: Session identifier
            user_id: Optional user ID for logged-in users
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
                'id': cart.id,
                'session_id': cart.session_id,
                'user_id': cart.user_id,
                'store_code': cart.store_code,
                'created_at': cart.created_at.isoformat() if cart.created_at else None,
                'updated_at': cart.updated_at.isoformat() if cart.updated_at else None
            }
            
        except Exception as e:
            logger.error(f"Error getting/creating cart: {str(e)}")
            result.status = False
            result.error = "Failed to get or create cart"
            result.details = str(e)
        
        return result
    
    @staticmethod
    def add_item_to_cart(cart_id: int, product_id: int, product_name: str, 
                        product_sku: str, selected_options: list, quantity: int = 1) -> Result:
        """
        Add item to cart.
        
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
            
            if cart_item:
                result.data = {
                    'id': cart_item.id,
                    'cart_id': cart_item.cart_id,
                    'product_id': cart_item.product_id,
                    'product_name': cart_item.product_name,
                    'product_sku': cart_item.product_sku,
                    'quantity': cart_item.quantity,
                    'unit_price': cart_item.unit_price,
                    'total_price': cart_item.total_price,
                    'created_at': cart_item.created_at.isoformat() if cart_item.created_at else None,
                    'updated_at': cart_item.updated_at.isoformat() if cart_item.updated_at else None
                }
            else:
                result.status = False
                result.error = "Failed to add item to cart"
            
        except Exception as e:
            logger.error(f"Error adding item to cart: {str(e)}")
            result.status = False
            result.error = "Failed to add item to cart"
            result.details = str(e)
        
            return result