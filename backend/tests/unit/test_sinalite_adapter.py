import time 
import pytest
import requests_mock
from requests.exceptions import Timeout, RequestException
from flask import Flask
from server.thirdparty.sinalite import SinaliteAdapter
from server.thirdparty.helpers import make_http_request

@pytest.fixture
def test_app():
    """Creating a Flask app with test config"""
    app = Flask(__name__)
    app.config["SINALITE_BASE_URL"] = "https://mockapi.sinalite.com"
    app.config["SINALITE_CLIENT_ID"] = "test_client"
    app.config["SINALITE_CLIENT_SECRET"] = "test_secret"
    return app

@pytest.fixture
def sinalite_adapter(test_app):
    """Initialize SinaliteAdapter with the test app"""
    adapter = SinaliteAdapter(test_app)
    adapter.init_app(test_app)
    return adapter

def test_constructor(test_app):
    """Test constructor with no Flask app"""
    adapter = SinaliteAdapter()
    assert adapter.base_url is None
    assert adapter.client_id is None
    assert adapter.client_secret is None

    adapter = SinaliteAdapter(test_app)
    assert adapter.base_url == test_app.config["SINALITE_BASE_URL"]
    assert adapter.client_id == test_app.config["SINALITE_CLIENT_ID"]
    assert adapter.client_secret == test_app.config["SINALITE_CLIENT_SECRET"]
    
def test_init_app(sinalite_adapter, test_app):
    """Tests that init correctly sets up the adapter"""

    adapter = SinaliteAdapter()
    assert adapter.base_url is None
    assert adapter.client_id is None
    assert adapter.client_secret is None

    adapter.init_app(test_app)
    assert sinalite_adapter.base_url == test_app.config["SINALITE_BASE_URL"]
    assert sinalite_adapter.client_id == test_app.config["SINALITE_CLIENT_ID"]
    assert sinalite_adapter.client_secret == test_app.config["SINALITE_CLIENT_SECRET"]

    # Ensure authentication is not called
    assert sinalite_adapter.access_token is None  
    assert sinalite_adapter.token_type is None
    assert sinalite_adapter.token_lifetime == 0
    assert sinalite_adapter.token_expiry == 0

    # Ensure name is set properly
    assert sinalite_adapter.name == "Sinalite"

def test_authentication_success(sinalite_adapter):
    """Test successful authentication using custom_base_url."""
    with requests_mock.Mocker() as mocker:
        mock_response = {
            "access_token": "mock_token",
            "token_type": "Bearer",
            "expires_in": 3600
        }
        # Using the custom_base_url for the test
        custom_base_url = "https://customapi.sinalite.com"
        url = f"{custom_base_url}/auth/token"
        mocker.post(url, json=mock_response, status_code=200)

        # Update the adapter to use a custom auth_base_url
        sinalite_adapter.auth_base_url = custom_base_url

        # Test the authenticate method
        assert sinalite_adapter.authenticate() is True
        assert sinalite_adapter.access_token == "mock_token"
        assert sinalite_adapter.token_type == "Bearer"
        assert sinalite_adapter.token_lifetime == 3600
        assert sinalite_adapter.token_expiry > time.time()

        # Confirm that the request was made to the custom_base_url
        assert mocker.called
        assert mocker.last_request.url == url

def test_token_expiry(sinalite_adapter):
    """Test token expiration logic"""
    sinalite_adapter.access_token = "valid_token"
    sinalite_adapter.token_expiry = time.time() - 10 # Expired token

    assert sinalite_adapter.is_access_expired() is True

def test_get_products_success(sinalite_adapter):
    """Test retrieving products successfully."""
    with requests_mock.Mocker() as mocker:
        sinalite_adapter.access_token = "valid_token"
        sinalite_adapter.token_type = "Bearer"
        sinalite_adapter.token_expiry = time.time() + 3600 # Token is valid
        mock_products = [
            {
                "id": 1,
                "name": "Business Cards"
            },
            {
                "id": 2,
                "name": "Flyers"
            }
        ]

        url = f"{sinalite_adapter.base_url}/product" 
        mocker.get(url, json=mock_products, status_code=200)
        products = sinalite_adapter.get_products()

        assert products == mock_products

def test_get_products_auth_failure(sinalite_adapter):
    """Test product retrieval failure due to authentication issue."""
    with requests_mock.Mocker() as mocker:
        # Set the custom auth_base_url
        sinalite_adapter.auth_base_url = "https://customapi.sinalite.com"
        auth_url = f"{sinalite_adapter.auth_base_url}/auth/token"
        
        mocker.post(auth_url, json={"access_token": "mock_token", "token_type": "Bearer", "expires_in": 3600}, status_code=200)

        # Mock the product retrieval request (using base_url, not auth_base_url)
        url = f"{sinalite_adapter.base_url}/product"
        mocker.get(url, json={"error": "Unauthorized"}, status_code=401)

        sinalite_adapter.access_token = None  # No valid token
        products = sinalite_adapter.get_products()
        
        # Assertions
        assert products == []

def test_authenticate_failure_scenarios(sinalite_adapter):
    """Test authentication failure with invalid credentials using both default and custom auth URLs."""
    with requests_mock.Mocker() as mocker:
        mock_response = {"message": "Invalid authentication request"}
        
        # Test with default base_url (set auth_base_url to match base_url for first test)
        sinalite_adapter.auth_base_url = sinalite_adapter.base_url
        default_url = f"{sinalite_adapter.base_url}/auth/token"
        mocker.post(default_url, json=mock_response, status_code=401)
        
        assert sinalite_adapter.authenticate() is False
        assert sinalite_adapter.access_token is None
        
        # Reset mocker for next test
        mocker.reset()
        
        # Test with custom auth_base_url
        sinalite_adapter.auth_base_url = "https://customapi.sinalite.com"
        custom_url = f"{sinalite_adapter.auth_base_url}/auth/token"
        mocker.post(custom_url, json=mock_response, status_code=401)
        
        assert sinalite_adapter.authenticate() is False
        assert sinalite_adapter.access_token is None

def test_get_product_categories(sinalite_adapter):
    """Test retrieving unique product categories."""
    with requests_mock.Mocker() as mocker:
        sinalite_adapter.access_token = "valid_token"
        sinalite_adapter.token_type = "Bearer"
        sinalite_adapter.token_expiry = time.time() + 3600  # Token is valid

        mock_products = [
            {"id": 1, "name": "Business Cards", "category": "Cards"},
            {"id": 2, "name": "Flyers", "category": "Marketing"},
            {"id": 3, "name": "Posters", "category": "Marketing"},
            {"id": 4, "name": "Brochures", "category": "Marketing"},
            {"id": 5, "name": "Stickers", "category": "Labels"},
        ]

        url = f"{sinalite_adapter.base_url}/product"
        mocker.get(url, json=mock_products, status_code=200)

        expected_categories = ["Cards", "Labels", "Marketing"] # Sorted in alphabetical order
        categories = sinalite_adapter.get_product_categories()

        # Check exact order and uniqueness without using set()
        assert len(categories) == 3
        assert len(categories) == len(set(categories))  
        assert categories[0] == expected_categories[0]
        assert categories[1] == expected_categories[1]
        assert categories[2] == expected_categories[2]