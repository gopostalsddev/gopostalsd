
import time
from flask import Flask
from server.thirdparty.helpers import logger, make_http_request

# Adapter class for interacting with the third party Sinlite API
class SinaliteAdapter:
    def __init__(self, app=None):
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
    
    def is_access_expired(self) -> bool:
        """Check if the access token is expired."""
        return time.time() >= self.token_expiry

    def init_app(self, app: Flask) -> bool:
        """Initialize the adapter with Flask app configuration."""
        self.base_url = app.config["SINALITE_BASE_URL"]
        self.client_id = app.config["SINALITE_CLIENT_ID"]
        self.client_secret = app.config["SINALITE_CLIENT_SECRET"]

    def authenticate(self):
        """Authenticate and obtain an access token."""
        
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "audience": "https://apiconnect.sinalite.com",
            "grant_type": "client_credentials"
        }
        
        response = make_http_request(self, "POST", "/auth/token", data=payload, requires_auth=False)

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

            if response:
                logger.error(f"{self.name} authentication failed!, Error: {response.get('message', 'No message provided')}")
            else:
                logger.error(f"{self.name} authentication failed! No response received.")

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