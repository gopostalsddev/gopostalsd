
import time
from flask import Flask
from server.thirdparty.helpers import logger, make_http_request
import os

# Adapter class for interacting with the third party Sinlite API
class SinaliteAdapter:
    def __init__(self, app=None):
        self.auth_base_url = None
        self.base_url = None
        self.client_id = None
        self.client_secret = None
        self.access_token = None 
        self.token_type = None
        self.token_lifetime = 0
        self.token_expiry = 0
        self.name = "Sinalite"

        if app:
            self.init_app(app)
        # Else init_app must be called with valid Flask app  before using the adapter
    
    def is_access_expired(self) -> bool:
        """Check if the access token is expired."""
        return time.time() >= self.token_expiry

    def init_app(self, app: Flask) -> bool:
        """Initialize the adapter with Flask app configuration."""
        self.auth_base_url = os.getenv("SINALITE_BASE_URL_DEV")
        self.base_url = app.config["SINALITE_BASE_URL"]
        self.client_id = app.config["SINALITE_CLIENT_ID"]
        self.client_secret = app.config["SINALITE_CLIENT_SECRET"]

        # Add to Flask extensions
        app.extensions["sinalite"] = self

    def authenticate(self):
        """Authenticate and obtain an access token."""
        
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "audience": "https://apiconnect.sinalite.com",
            "grant_type": "client_credentials"
        }
        
        
        response = make_http_request(self, "POST", "/auth/token", data=payload, requires_auth=False, custom_base_url=self.auth_base_url)

        if response and "access_token" in response:
            self.access_token = response.get("access_token")
            self.token_type = response.get("token_type", "")
            self.token_lifetime= response.get("expires_in", 3600) # Default renewal to 1 Hour
            self.token_expiry = time.time() + self.token_lifetime

            logger.info(f"{self.name} authentication successful!")
            return True
        else:
            self.access_token = None
            self.token_type = None
            self.token_lifetime= 0
            self.token_expiry = 0
            
            logger.error(f"{self.name} authentication failed!")
            return False

    def get_products(self):
        """Fetch available products from Sinalite API using the helper function."""
        response = make_http_request(self, "GET", "/product", requires_auth=True)

        if response:
            return response # Returns valid product data
        
        logger.error(f"{self.name} failed to retrieve products")
        return []
    
    def get_product_categories(self):
        """Fetch available product categories"""
        products = self.get_products()
        return sorted({product["category"] for product in products})
    
    def get_product_details(self, product_id, store_code):
        """
        Fetch detailed product information including options and pricing data.
        Returns the 3-array structure from Sinalite API.

        Args:
            product_id (int): The product ID
            store_code (int): Store code (6 for Canada, 9 for US)

        Returns:
            dict: Product details with options, pricing combinations, and metadata
        """
        endpoint = f"/product/{product_id}/{store_code}"
        response = make_http_request(self, "GET", endpoint, requires_auth=True)

        if response:
            return response

        logger.error(f"{self.name} failed to retrieve product details for ID {product_id}")
        return None
    
    def get_product_price(self, product_id, store_code, product_options):
        """
        Get pricing information for a specific product configuration.
        
        Args:
            product_id (int): The product ID
            store_code (int): Store code (6 for Canada, 9 for US)
            product_options (list): List of option IDs
            
        Returns:
            dict: Price and package information
        """
        endpoint = f"/price/{product_id}/{store_code}"
        payload = {"productOptions": product_options}
        
        response = make_http_request(self, "POST", endpoint, data=payload, requires_auth=True)
        
        if response:
            return response
        
        logger.error(f"{self.name} failed to retrieve pricing for product ID {product_id}")
        return None
    
    def get_product_variants(self, product_id, offset=0):
        """
        Get product variants with pricing information.
        
        Args:
            product_id (int): The product ID
            offset (int): Offset for pagination (default 0)
            
        Returns:
            list: List of variants with prices and keys
        """
        endpoint = f"/variants/{product_id}/{offset}"
        response = make_http_request(self, "GET", endpoint, requires_auth=True)
        
        if response:
            return response
        
        logger.error(f"{self.name} failed to retrieve variants for product ID {product_id}")
        return []
    
    def get_price_by_key(self, product_id, key):
        """
        Get variant price using product ID and key.
        
        Args:
            product_id (int): The product ID
            key (str): The variant key
            
        Returns:
            dict: Price information
        """
        endpoint = f"/pricebykey/{product_id}/{key}"
        response = make_http_request(self, "GET", endpoint, requires_auth=True)
        
        if response:
            return response
        
        logger.error(f"{self.name} failed to retrieve price for product ID {product_id} with key {key}")
        return None
    
    def get_shipping_estimate(self, items, shipping_info):
        """
        Get shipping estimates for cart items.
        
        Args:
            items (list): List of cart items with productId and options
            shipping_info (dict): Shipping destination information
            
        Returns:
            list: Available shipping options with prices and delivery times
        """
        endpoint = "/order/shippingEstimate"
        payload = {
            "items": items,
            "shippingInfo": shipping_info
        }
        
        # Debug logging
        logger.info(f"Sending shipping estimate request to Sinalite API:")
        logger.info(f"Items: {items}")
        logger.info(f"Shipping Info: {shipping_info}")
        logger.info(f"Full payload: {payload}")
        
        response = make_http_request(self, "POST", endpoint, data=payload, requires_auth=True)
        
        if response and "body" in response:
            logger.info(f"Shipping estimate response: {response}")
            return response["body"]
        elif response and isinstance(response, list):
            # Handle case where response is directly an array
            logger.info(f"Shipping estimate response (direct array): {response}")
            return response
        
        logger.error(f"{self.name} failed to retrieve shipping estimates")
        return []