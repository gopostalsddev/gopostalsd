import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from server.config import database as db
from server import create_server
from server.factories.main_factory import MainFactory
from server.thirdparty.sinalite import SinaliteAdapter
from server.services.pricing_service import PricingService
from server.services.cart_service import CartService
from server.repositories.pricing_repository import PricingRepository
from server.repositories.cart_repository import CartRepository


# Define the app fixture required by pytest-flask
@pytest.fixture
def app():
    """Create a Flask application instance in testing mode."""
    # Create a temporary database file for testing
    db_fd, db_path = tempfile.mkstemp()
    
    # Create a Flask application instance in testing mode
    test_app = create_server("testing")
    test_app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    test_app.config['TESTING'] = True
    
    # Set up the application context
    with test_app.app_context():
        # Create tables
        db.create_all()
        yield test_app
        db.drop_all()
    
    # Clean up the temporary database file
    os.close(db_fd)
    os.unlink(db_path)


# Define the client fixture that depends on the app fixture
@pytest.fixture
def client(app):
    """Create a test client for making requests."""
    return app.test_client()


# Factory fixtures for dependency injection
@pytest.fixture
def mock_sinalite_adapter():
    """Create a mock Sinalite adapter for testing."""
    mock_adapter = Mock(spec=SinaliteAdapter)
    mock_adapter.name = "MockSinalite"
    return mock_adapter


@pytest.fixture
def pricing_repository():
    """Create a pricing repository instance for testing."""
    return PricingRepository()


@pytest.fixture
def cart_repository():
    """Create a cart repository instance for testing."""
    return CartRepository()


@pytest.fixture
def pricing_service(mock_sinalite_adapter, pricing_repository):
    """Create a pricing service instance for testing."""
    return PricingService(mock_sinalite_adapter, pricing_repository)


@pytest.fixture
def cart_service(pricing_service, cart_repository):
    """Create a cart service instance for testing."""
    return CartService(pricing_service, cart_repository)


@pytest.fixture
def main_factory():
    """Create a main factory instance for testing."""
    return MainFactory()


# Mock data fixtures
@pytest.fixture
def sample_product_options():
    """Sample product options data for testing."""
    return [
        {
            "group": "qty",
            "options": [
                {"id": 5, "name": "50"},
                {"id": 105, "name": "25"},
                {"id": 10, "name": "10"}
            ]
        },
        {
            "group": "Stock",
            "options": [
                {"id": 447, "name": "Brown Cardboard"},
                {"id": 448, "name": "White Cardboard"}
            ]
        }
    ]


@pytest.fixture
def sample_pricing_data():
    """Sample pricing data for testing."""
    return {
        "price": 22.51,
        "currency": "USD",
        "estimated_ship_date": "2024-01-15"
    }


@pytest.fixture
def sample_cart_data():
    """Sample cart data for testing."""
    return {
        "id": 1,
        "session_id": "test_session_123",
        "user_id": None,
        "store_code": 6,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def sample_cart_item_data():
    """Sample cart item data for testing."""
    return {
        "id": 1,
        "cart_id": 1,
        "product_id": 123,
        "product_name": "Test Product",
        "product_sku": "TEST-001",
        "quantity": 2,
        "unit_price": 10.50,
        "total_price": 21.00,
        "selected_options": [5, 447],
        "option_key": "5-447"
    }


@pytest.fixture
def sample_shipping_estimates():
    """Sample shipping estimates data for testing."""
    return [
        ["UPS", "UPS Standard", 9.1, 1],
        ["UPS", "UPS Expedited", 12.82, 1],
        ["FedEx", "FedEx Standard Overnight", 9.67, 1]
    ]


# Error fixtures
@pytest.fixture
def mock_database_error():
    """Mock database error for testing error handling."""
    return Exception("Database connection failed")


@pytest.fixture
def mock_api_error():
    """Mock API error for testing error handling."""
    return Exception("External API request failed")


# Performance testing fixtures
@pytest.fixture
def large_dataset():
    """Large dataset for performance testing."""
    return {
        "products": [{"id": i, "name": f"Product {i}"} for i in range(1000)],
        "options": [{"id": i, "name": f"Option {i}"} for i in range(100)]
    }
