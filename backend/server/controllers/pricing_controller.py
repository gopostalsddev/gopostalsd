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
            
            result.status = True
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
    def calculate_price(product_id: int, options: list, store_code: int, customization: dict | None = None) -> Result:
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
            
            pricing = pricing_service.calculate_product_price(product_id, options, store_code, customization)
            
            if not pricing:
                result.status = False
                result.error = "Failed to calculate price"
                return result
            
            result.status = True
            result.data = pricing
            
        except Exception as e:
            logger.error(f"Error calculating price: {str(e)}")
            result.status = False
            result.error = "Failed to calculate price"
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

            if not estimates:
                result.status = False
                result.error = "Shipping estimates are currently unavailable from the provider"
                return result
            
            result.status = True
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
