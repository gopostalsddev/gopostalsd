"""
Test utilities and helpers for comprehensive testing.
"""

import pytest
import json
import time
from unittest.mock import Mock, patch, MagicMock
from server.controllers.helpers import Result


class TestResult:
    """Test cases for Result class."""

    def test_result_success(self):
        """Test successful result creation."""
        data = {"test": "data"}
        result = Result(status=True, data=data)
        
        assert result.status is True
        assert result.data == data
        assert result.error is None
        assert result.details is None

    def test_result_error(self):
        """Test error result creation."""
        error = "Test error"
        details = "Test details"
        result = Result(status=False, error=error, details=details)
        
        assert result.status is False
        assert result.error == error
        assert result.details == details
        assert result.data is None

    def test_result_default_values(self):
        """Test result with default values."""
        result = Result()
        
        assert result.status is True
        assert result.data is None
        assert result.error is None
        assert result.details is None

    def test_result_to_dict(self):
        """Test result conversion to dictionary."""
        data = {"test": "data"}
        result = Result(status=True, data=data)
        
        result_dict = result.to_dict()
        
        assert result_dict["status"] is True
        assert result_dict["data"] == data
        assert "error" not in result_dict
        assert "details" not in result_dict

    def test_result_to_dict_with_error(self):
        """Test error result conversion to dictionary."""
        error = "Test error"
        details = "Test details"
        result = Result(status=False, error=error, details=details)
        
        result_dict = result.to_dict()
        
        assert result_dict["status"] is False
        assert result_dict["error"] == error
        assert result_dict["details"] == details
        assert "data" not in result_dict


class TestMockHelpers:
    """Test cases for mock helper functions."""

    def test_create_mock_sinalite_adapter(self):
        """Test mock Sinalite adapter creation."""
        from tests.conftest import mock_sinalite_adapter
        
        adapter = mock_sinalite_adapter()
        
        assert adapter.name == "MockSinalite"
        assert hasattr(adapter, 'get_product_options')
        assert hasattr(adapter, 'calculate_price')
        assert hasattr(adapter, 'get_shipping_estimates')

    def test_create_mock_repository(self):
        """Test mock repository creation."""
        from tests.conftest import pricing_repository
        
        repo = pricing_repository()
        
        assert hasattr(repo, 'get_cached_options')
        assert hasattr(repo, 'cache_options')
        assert hasattr(repo, 'get_cached_pricing')
        assert hasattr(repo, 'cache_variants')

    def test_create_mock_service(self):
        """Test mock service creation."""
        from tests.conftest import pricing_service
        
        service = pricing_service()
        
        assert hasattr(service, 'get_product_options')
        assert hasattr(service, 'calculate_price')
        assert hasattr(service, 'get_shipping_estimates')

    def test_sample_data_fixtures(self):
        """Test sample data fixtures."""
        from tests.conftest import sample_product_options, sample_pricing_data, sample_cart_data
        
        # Test product options
        options = sample_product_options()
        assert isinstance(options, list)
        assert len(options) > 0
        assert "group" in options[0]
        assert "options" in options[0]
        
        # Test pricing data
        pricing = sample_pricing_data()
        assert isinstance(pricing, dict)
        assert "price" in pricing
        assert "currency" in pricing
        
        # Test cart data
        cart = sample_cart_data()
        assert isinstance(cart, dict)
        assert "id" in cart
        assert "session_id" in cart


class TestDatabaseHelpers:
    """Test cases for database helper functions."""

    def test_create_test_database(self, app):
        """Test test database creation."""
        from server.config import database as db
        
        with app.app_context():
            # Check that tables exist
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            # Should have some tables
            assert len(tables) > 0

    def test_cleanup_test_database(self, app):
        """Test test database cleanup."""
        from server.config import database as db
        
        with app.app_context():
            # Create some test data
            db.session.execute("CREATE TABLE IF NOT EXISTS test_table (id INTEGER)")
            
            # Cleanup should work
            db.drop_all()
            
            # Verify cleanup
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            assert "test_table" not in tables


class TestAPITestHelpers:
    """Test cases for API test helper functions."""

    def test_make_api_request(self, client):
        """Test API request helper."""
        with patch('server.routes.pricing_routes.PricingController.get_product_options') as mock_controller:
            mock_controller.return_value = Result(status=True, data=[])
            
            response = client.get('/api/pricing/products/123/options?store_code=6')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] is True

    def test_validate_api_response(self, client):
        """Test API response validation helper."""
        with patch('server.routes.pricing_routes.PricingController.get_product_options') as mock_controller:
            mock_controller.return_value = Result(status=True, data=[{"test": "data"}])
            
            response = client.get('/api/pricing/products/123/options?store_code=6')
            
            # Validate response structure
            assert response.status_code == 200
            data = json.loads(response.data)
            assert "status" in data
            assert "data" in data
            assert data["status"] is True
            assert isinstance(data["data"], list)

    def test_validate_error_response(self, client):
        """Test error response validation helper."""
        with patch('server.routes.pricing_routes.PricingController.get_product_options') as mock_controller:
            mock_controller.return_value = Result(status=False, error="Test error")
            
            response = client.get('/api/pricing/products/123/options?store_code=6')
            
            # Validate error response structure
            assert response.status_code == 400
            data = json.loads(response.data)
            assert "status" in data
            assert "error" in data
            assert data["status"] is False
            assert data["error"] == "Test error"


class TestPerformanceHelpers:
    """Test cases for performance test helper functions."""

    def test_measure_execution_time(self):
        """Test execution time measurement helper."""
        def slow_function():
            time.sleep(0.1)
            return "done"
        
        start_time = time.time()
        result = slow_function()
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        assert result == "done"
        assert execution_time >= 0.1
        assert execution_time < 0.2  # Should be close to 0.1 seconds

    def test_concurrent_execution(self):
        """Test concurrent execution helper."""
        def worker_function(worker_id):
            time.sleep(0.01)
            return f"worker_{worker_id}"
        
        num_workers = 5
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(worker_function, i) for i in range(num_workers)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # All workers should complete
        assert len(results) == num_workers
        assert all(f"worker_{i}" in results for i in range(num_workers))
        
        # Should complete faster than sequential execution
        assert execution_time < 0.1  # Much faster than 5 * 0.01 = 0.05 seconds

    def test_memory_usage_measurement(self):
        """Test memory usage measurement helper."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Create some data to increase memory usage
        large_list = [i for i in range(10000)]
        
        current_memory = process.memory_info().rss
        memory_increase = current_memory - initial_memory
        
        # Memory should have increased
        assert memory_increase > 0
        
        # Cleanup
        del large_list


class TestDataValidationHelpers:
    """Test cases for data validation helper functions."""

    def test_validate_product_id(self):
        """Test product ID validation helper."""
        from server.controllers.pricing_controller import PricingController
        
        # Valid IDs
        assert PricingController.validate_product_id(123) is True
        assert PricingController.validate_product_id(1) is True
        
        # Invalid IDs
        assert PricingController.validate_product_id(None) is False
        assert PricingController.validate_product_id(0) is False
        assert PricingController.validate_product_id(-1) is False
        assert PricingController.validate_product_id("invalid") is False

    def test_validate_options(self):
        """Test options validation helper."""
        from server.controllers.pricing_controller import PricingController
        
        # Valid options
        assert PricingController.validate_options([5, 447]) is True
        assert PricingController.validate_options([1]) is True
        
        # Invalid options
        assert PricingController.validate_options([]) is False
        assert PricingController.validate_options(None) is False
        assert PricingController.validate_options("invalid") is False

    def test_validate_cart_id(self):
        """Test cart ID validation helper."""
        from server.controllers.pricing_controller import PricingController
        
        # Valid IDs
        assert PricingController.validate_cart_id(1) is True
        assert PricingController.validate_cart_id(123) is True
        
        # Invalid IDs
        assert PricingController.validate_cart_id(None) is False
        assert PricingController.validate_cart_id(0) is False
        assert PricingController.validate_cart_id(-1) is False
        assert PricingController.validate_cart_id("invalid") is False
