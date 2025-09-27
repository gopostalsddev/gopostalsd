import pytest
import requests_mock
import time
from requests.exceptions import Timeout, RequestException
from server.thirdparty.helpers import make_http_request

@pytest.fixture
def mock_adapter():
    """Mock third-party adapter with necessary attributes."""
    class MockAdapter:
        base_url = "https://mockapi.sinalite.com"
        token_type = "Bearer"
        access_token = "mock_token"
        token_expiry = time.time() + 3600  # Token is valid
        name = "MockAdapter"

        def is_access_expired(self):
            return time.time() >= self.token_expiry

    return MockAdapter()

def test_make_http_request_success(mock_adapter):
    """Test successful request with authentication."""
    with requests_mock.Mocker() as mocker:
        url = f"{mock_adapter.base_url}/test-endpoint"
        mock_response = {"message": "Success"}
        mocker.get(url, json=mock_response, status_code=200)

        response = make_http_request(mock_adapter, "GET", "/test-endpoint", requires_auth=True)

        assert response == mock_response

def test_make_http_request_auth_failure(mock_adapter):
    """Test request failure due to authentication error (401)."""
    with requests_mock.Mocker() as mocker:
        url = f"{mock_adapter.base_url}/test-endpoint"
        mocker.get(url, json={"error": "Unauthorized"}, status_code=401)

        response = make_http_request(mock_adapter, "GET", "/test-endpoint", requires_auth=True)

        assert response is None

def test_make_http_request_rate_limiting_with_retry(mock_adapter):
    """Test API rate limiting (429) with automatic retry."""
    with requests_mock.Mocker() as mocker:
        url = f"{mock_adapter.base_url}/test-endpoint"
        mocker.get(url, [
            {"json": {"error": "Rate limit exceeded"}, "status_code": 429},  # First attempt
            {"json": {"message": "Success"}, "status_code": 200},  # Second attempt
        ])

        response = make_http_request(mock_adapter, "GET", "/test-endpoint", requires_auth=True)

        assert response == {"message": "Success"}

def test_make_http_request_server_error_with_retry(mock_adapter):
    """Test API handling of server errors (500) with retries."""
    with requests_mock.Mocker() as mocker:
        url = f"{mock_adapter.base_url}/test-endpoint"
        mocker.get(url, [
            {"json": {}, "status_code": 500},  # First attempt
            {"json": {}, "status_code": 500},  # Second attempt
            {"json": {"message": "Success"}, "status_code": 200},  # Third attempt
        ])

        response = make_http_request(mock_adapter, "GET", "/test-endpoint", requires_auth=True)

        assert response == {"message": "Success"}

def test_make_http_request_service_unavailable_with_retry(mock_adapter):
    """Test API handling of service unavailable (503) with retries."""
    with requests_mock.Mocker() as mocker:
        url = f"{mock_adapter.base_url}/test-endpoint"
        mocker.get(url, [
            {"json": {}, "status_code": 503},  # First attempt
            {"json": {}, "status_code": 503},  # Second attempt
            {"json": {"message": "Success"}, "status_code": 200},  # Third attempt
        ])

        response = make_http_request(mock_adapter, "GET", "/test-endpoint", requires_auth=True)

        assert response == {"message": "Success"}

def test_make_http_request_max_retries_reached(mock_adapter):
    """Test failure after max retries are exhausted."""
    with requests_mock.Mocker() as mocker:
        url = f"{mock_adapter.base_url}/test-endpoint"
        mocker.get(url, [
            {"json": {}, "status_code": 500},  # First attempt
            {"json": {}, "status_code": 500},  # Second attempt
            {"json": {}, "status_code": 500},  # Third attempt
        ])

        response = make_http_request(mock_adapter, "GET", "/test-endpoint", requires_auth=True)

        assert response is None

def test_make_http_request_timeout(mock_adapter):
    """Test request timeout handling."""
    with requests_mock.Mocker() as mocker:
        url = f"{mock_adapter.base_url}/test-endpoint"
        mocker.get(url, exc=Timeout)

        response = make_http_request(mock_adapter, "GET", "/test-endpoint", requires_auth=True)

        assert response is None

def test_make_http_request_general_request_exception(mock_adapter):
    """Test handling of a general request exception."""
    with requests_mock.Mocker() as mocker:
        url = f"{mock_adapter.base_url}/test-endpoint"
        mocker.get(url, exc=RequestException)

        response = make_http_request(mock_adapter, "GET", "/test-endpoint", requires_auth=True)

        assert response is None

def test_make_http_request_with_custom_base_url(mock_adapter):
    """Test that custom_base_url is used when provided."""
    with requests_mock.Mocker() as mocker:
        custom_base_url = "https://customapi.sinalite.com"
        url = f"{custom_base_url}/test-endpoint"
        mock_response = {"message": "Custom Base URL Success"}
        mocker.get(url, json=mock_response, status_code=200)

        # Invoke make_http_request with custom_base_url
        response = make_http_request(
            mock_adapter,
            "GET",
            "/test-endpoint",
            requires_auth=True,
            custom_base_url=custom_base_url
        )

        # Assertions
        assert response == mock_response
