import time 
import pytest
import requests_mock
from requests.exceptions import Timeout
from flask import Flask
from server.thirdparty.sinalite import SinaliteAdapter

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
