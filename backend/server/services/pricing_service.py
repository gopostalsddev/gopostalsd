"""
Pricing Service for Go Postal SD Application

This service implements the Strategy and Factory design patterns to handle
product pricing, cart management, and shipping calculations using the Sinalite API.

The service provides a clean abstraction layer for pricing operations and
implements caching strategies to optimize API usage and performance.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import logging
from server import database as db
from server.models.pricing import (
    ProductOption, ProductPricing, 
    ShippingOption, ProductVariant, StoreCode
)
from server.thirdparty.sinalite import SinaliteAdapter
from server.exceptions.pricing_exceptions import (
    ProductNotFoundError, PricingCalculationError, 
    InvalidOptionsError, ShippingEstimateError
)
from server.repositories.pricing_repository import PricingRepository

logger = logging.getLogger(__name__)


class PricingStrategy(ABC):
    """
    Abstract base class for pricing strategies.
    Implements the Strategy pattern to allow different pricing approaches.
    """
    
    @abstractmethod
    def calculate_price(self, product_id: int, options: List[int], store_code: int) -> Optional[Dict]:
        """Calculate price for a product with given options."""
        pass


class SinalitePricingStrategy(PricingStrategy):
    """
    Concrete pricing strategy that uses the Sinalite API for pricing calculations.
    Implements caching to reduce API calls and improve performance.
    """
    
    def __init__(self, sinalite_adapter: SinaliteAdapter, repository: PricingRepository):
        self.sinalite = sinalite_adapter
        self.repository = repository
        self.cache_duration = timedelta(hours=1)  # Cache pricing for 1 hour
    
    def calculate_price(self, product_id: int, options: List[int], store_code: int) -> Optional[Dict]:
        """
        Calculate price using Sinalite API key-based pricing with caching.
        
        Args:
            product_id: Sinalite product ID
            options: List of selected option IDs
            store_code: Store code (6 for Canada, 9 for US)
            
        Returns:
            Dict containing price and package information, or None if failed
        """
        try:
            # Create option key for caching (sorted for consistency)
            option_key = "-".join(map(str, sorted(options)))
            
            # Check cache first
            cached_pricing = self.repository.get_cached_pricing(product_id, store_code, option_key)
            if cached_pricing:
                logger.info(f"Using cached pricing for product {product_id}")
                return cached_pricing
            
            # Use key-based pricing from Sinalite API
            pricing_data = self.sinalite.get_price_by_key(product_id, option_key)
            if not pricing_data:
                logger.error(f"Failed to get pricing for product {product_id} with key {option_key}")
                return None
            
            # Handle the response format - Sinalite returns a list with price dict
            price_value = 0
            if isinstance(pricing_data, list) and len(pricing_data) > 0:
                price_value = pricing_data[0].get('price', 0)
            elif isinstance(pricing_data, dict):
                price_value = pricing_data.get('price', 0)
            
            # Format the response to match expected structure
            formatted_pricing = {
                'price': price_value,
                'packageInfo': {},  # Will be populated from product details if needed
                'productOptions': options
            }
            
            # Cache the result
            self.repository.cache_pricing(product_id, store_code, option_key, formatted_pricing, options)
            
            return formatted_pricing
            
        except Exception as e:
            logger.error(f"Error calculating price for product {product_id}: {str(e)}")
            return None
    


class PricingService:
    """
    Main pricing service that coordinates pricing operations.
    Implements the Facade pattern to provide a simple interface for complex operations.
    """
    
    def __init__(self, sinalite_adapter: SinaliteAdapter, repository: PricingRepository):
        self.sinalite = sinalite_adapter
        self.repository = repository
        self.pricing_strategy = SinalitePricingStrategy(sinalite_adapter, repository)
    
    def get_product_options(self, product_id: int, store_code: int) -> List[Dict]:
        """
        Get available options for a product.
        
        Args:
            product_id: Sinalite product ID
            store_code: Store code (6 for Canada, 9 for US)
            
        Returns:
            List of product options grouped by category
        """
        try:
            # Check cache first
            cached_options = self.repository.get_cached_options(product_id)
            if cached_options:
                return self._group_options_by_category(cached_options)
            
            # Fetch from API
            product_details = self.sinalite.get_product_details(product_id, store_code)
            if not product_details or len(product_details) < 1:
                logger.error(f"No product details found for product {product_id}")
                return []
            
            options = product_details[0]  # First array contains options
            
            # Cache the options
            self.repository.cache_options(product_id, options)
            
            # Group options by category
            grouped_options = self._group_options_by_category(options)
            return grouped_options
            
        except Exception as e:
            logger.error(f"Error getting product options for product {product_id}: {str(e)}")
            return []
    
    def get_product_variants(self, product_id: int, offset: int = 0) -> List[Dict]:
        """
        Get product variants with pricing.
        
        Args:
            product_id: Sinalite product ID
            offset: Pagination offset
            
        Returns:
            List of variants with prices and keys
        """
        try:
            # Check cache first
            cached_variants = self._get_cached_variants(product_id, offset)
            if cached_variants:
                return cached_variants
            
            # Fetch from API
            variants = self.sinalite.get_product_variants(product_id, offset)
            if not variants:
                logger.error(f"No variants found for product {product_id}")
                return []
            
            # Cache the variants
            self._cache_variants(product_id, offset, variants)
            
            return variants
            
        except Exception as e:
            logger.error(f"Error getting product variants for product {product_id}: {str(e)}")
            return []
    
    def calculate_product_price(self, product_id: int, options: List[int], store_code: int) -> Optional[Dict]:
        """
        Calculate price for a product with selected options.
        
        Args:
            product_id: Sinalite product ID
            options: List of selected option IDs
            store_code: Store code (6 for Canada, 9 for US)
            
        Returns:
            Dict containing price and package information
        """
        return self.pricing_strategy.calculate_price(product_id, options, store_code)
    
    def get_shipping_estimates(self, cart_items: List[Dict], shipping_info: Dict) -> List[Dict]:
        """
        Get shipping estimates for cart items.
        
        Args:
            cart_items: List of cart items with productId and options
            shipping_info: Shipping destination information
            
        Returns:
            List of available shipping options
        """
        try:
            logger.info(f"PricingService.get_shipping_estimates called with:")
            logger.info(f"cart_items: {cart_items}")
            logger.info(f"shipping_info: {shipping_info}")
            
            # Prepare items for API call - handle both old and new formats
            api_items = []
            for item in cart_items:
                # Handle new format (from frontend) or old format (from cart)
                if 'productId' in item:
                    api_items.append({
                        'productId': item['productId'],
                        'options': item['options']
                    })
                else:
                    api_items.append({
                        'productId': item['product_id'],
                        'options': item['selected_options']
                    })
            
            logger.info(f"Prepared api_items: {api_items}")
            
            # Get shipping estimates from API
            estimates = self.sinalite.get_shipping_estimate(api_items, shipping_info)
            
            logger.info(f"Raw estimates from Sinalite: {estimates}")
            
            # Check if we got valid estimates
            if not estimates or len(estimates) == 0:
                logger.error("No shipping estimates received from Sinalite API")
                logger.error("This indicates an API issue that should be investigated")
                return self._get_fallback_shipping_options()
            
            # Format response according to Sinalite API documentation
            # Response format: [["UPS", "UPS Standard", 9.1, 1], ...]
            shipping_options = []
            for estimate in estimates:
                if isinstance(estimate, list) and len(estimate) >= 4:
                    shipping_options.append({
                        'carrier_name': estimate[0],
                        'method_name': estimate[1],
                        'price': float(estimate[2]),
                        'shipping_days': int(estimate[3])
                    })
            
            # If no valid estimates were parsed, log error
            if not shipping_options:
                logger.error("No valid shipping estimates parsed from Sinalite API response")
                logger.error("This indicates a data format issue that should be investigated")
                return self._get_fallback_shipping_options()
            
            logger.info(f"Formatted shipping_options: {shipping_options}")
            return shipping_options
            
        except Exception as e:
            logger.error(f"Unexpected error getting shipping estimates: {str(e)}")
            logger.error("This should be investigated for production stability")
            return self._get_fallback_shipping_options()
    
    def _get_fallback_shipping_options(self) -> List[Dict]:
        """
        Return empty list when Sinalite API is unavailable.
        We don't want to show estimated costs in production as they could be misleading.
        """
        logger.error("Sinalite API unavailable - shipping estimates not available")
        logger.error("This should be investigated and resolved for production use")
        return []
    
    
    def _group_options_by_category(self, options: List[Dict]) -> List[Dict]:
        """Group options by their category/group."""
        grouped = {}
        for option in options:
            group = option.get('group', 'Other')
            if group not in grouped:
                grouped[group] = []
            grouped[group].append(option)
        
        # Convert to list format
        result = []
        for group, group_options in grouped.items():
            result.append({
                'group': group,
                'options': group_options
            })
        
        return result
    


