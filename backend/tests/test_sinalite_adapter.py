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
    adapter = SinaliteAdapter()
    adapter.init_app(test_app)
    return adapter

def test_init_app(sinalite_adapter, test_app):
    """Tests that init correctly sets up the adapter"""

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
    """Test successful authentication"""
    with requests_mock.Mocker() as mocker:
        mock_response = {
            "access_token": "mock_token",
            "token_type": "Bearer",
            "expires_in": 3600
        }
        url = f"{sinalite_adapter.base_url}/auth/token"
        mocker.post(url, json=mock_response, status_code=200)

        assert sinalite_adapter.authenticate() is True
        assert sinalite_adapter.access_token == "mock_token"
        assert sinalite_adapter.token_type == "Bearer"
        assert sinalite_adapter.token_lifetime == 3600
        assert sinalite_adapter.token_expiry > time.time()

def test_authenticate_invalid_credentials(sinalite_adapter):
    """Test authentication failure with invalid credentials."""
    with requests_mock.Mocker() as mocker:
        mock_response = {"message": "Invalid authentication request"}
        url = f"{sinalite_adapter.base_url}/auth/token"
        mocker.post(url, json=mock_response, status_code=401)

        assert sinalite_adapter.authenticate() is False
        assert sinalite_adapter.access_token is None

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

        url = f"{sinalite_adapter.base_url}/products" 
        mocker.get(url, json=mock_products, status_code=200)
        products = sinalite_adapter.get_products()

        assert products == mock_products

def test_get_products_auth_failure(sinalite_adapter):
    """Test product retrieval failure due to authentication issue"""
    with requests_mock.Mocker() as mocker:
        sinalite_adapter.access_token = None # No valid token

        # Mock authentication request
        auth_url = f"{sinalite_adapter.base_url}/auth/token"
        mocker.post(auth_url, json={"access_token": "mock_token", "token_type": "Bearer", "expires_in": 3600}, status_code=200)

        url = f"{sinalite_adapter.base_url}/products" 
        mocker.get(url, json={"error": "Unauthorized"}, status_code=401)

        products = sinalite_adapter.get_products()
        assert products == []
