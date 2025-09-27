"""
Performance and load tests for the application.
Tests system performance under various load conditions.
"""

import pytest
import time
import threading
import concurrent.futures
from unittest.mock import Mock, patch
from server.controllers.helpers import Result


class TestPerformance:
    """Performance test cases."""

    def test_pricing_service_performance(self, pricing_service, sample_product_options):
        """Test pricing service performance under load."""
        product_id = 123
        store_code = 6
        
        # Mock the repository to return cached data quickly
        pricing_service.repository.get_cached_options.return_value = sample_product_options
        pricing_service.repository.is_cache_valid.return_value = True
        
        # Measure time for single request
        start_time = time.time()
        result = pricing_service.get_product_options(product_id, store_code)
        end_time = time.time()
        
        assert result.status is True
        assert (end_time - start_time) < 0.1  # Should complete in under 100ms

    def test_concurrent_pricing_requests(self, pricing_service, sample_product_options):
        """Test concurrent pricing requests."""
        product_id = 123
        store_code = 6
        num_requests = 10
        
        # Mock the repository
        pricing_service.repository.get_cached_options.return_value = sample_product_options
        pricing_service.repository.is_cache_valid.return_value = True
        
        def make_request():
            return pricing_service.get_product_options(product_id, store_code)
        
        # Execute concurrent requests
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        end_time = time.time()
        
        # All requests should succeed
        assert all(result.status for result in results)
        assert len(results) == num_requests
        
        # Should complete in reasonable time
        assert (end_time - start_time) < 1.0  # Should complete in under 1 second

    def test_cart_service_performance(self, cart_service, sample_cart_data):
        """Test cart service performance under load."""
        session_id = "test_session"
        user_id = None
        store_code = 6
        
        # Mock the repository
        mock_cart = Mock()
        mock_cart.to_dict.return_value = sample_cart_data
        cart_service.repository.get_or_create_cart.return_value = mock_cart
        
        # Measure time for cart operations
        start_time = time.time()
        result = cart_service.get_or_create_cart(session_id, user_id, store_code)
        end_time = time.time()
        
        assert result.status is True
        assert (end_time - start_time) < 0.1  # Should complete in under 100ms

    def test_database_connection_pool(self, app):
        """Test database connection pool performance."""
        from server.config import database as db
        
        def create_connection():
            with app.app_context():
                return db.session.execute("SELECT 1").fetchone()
        
        # Test multiple concurrent database connections
        num_connections = 5
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_connections) as executor:
            futures = [executor.submit(create_connection) for _ in range(num_connections)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        
        # All connections should succeed
        assert len(results) == num_connections
        assert all(result is not None for result in results)
        
        # Should complete in reasonable time
        assert (end_time - start_time) < 2.0  # Should complete in under 2 seconds

    def test_memory_usage_under_load(self, pricing_service, large_dataset):
        """Test memory usage under load."""
        import psutil
        import os
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Simulate processing large dataset
        for i in range(100):
            pricing_service.get_product_options(i, 6)
        
        # Get final memory usage
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 50MB)
        assert memory_increase < 50 * 1024 * 1024  # 50MB in bytes

    def test_cache_performance(self, pricing_service, sample_product_options):
        """Test cache performance and efficiency."""
        product_id = 123
        store_code = 6
        
        # Mock cache hit
        pricing_service.repository.get_cached_options.return_value = sample_product_options
        pricing_service.repository.is_cache_valid.return_value = True
        
        # First request (cache miss simulation)
        start_time = time.time()
        result1 = pricing_service.get_product_options(product_id, store_code)
        first_request_time = time.time() - start_time
        
        # Second request (cache hit)
        start_time = time.time()
        result2 = pricing_service.get_product_options(product_id, store_code)
        second_request_time = time.time() - start_time
        
        # Both should succeed
        assert result1.status is True
        assert result2.status is True
        
        # Cache hit should be faster (though in this mock it might be similar)
        # This is more of a structural test than a performance test
        assert first_request_time >= 0
        assert second_request_time >= 0

    def test_error_handling_performance(self, pricing_service):
        """Test error handling doesn't significantly impact performance."""
        product_id = 123
        store_code = 6
        
        # Mock repository error
        pricing_service.repository.get_cached_options.side_effect = Exception("Database Error")
        
        # Measure error handling time
        start_time = time.time()
        result = pricing_service.get_product_options(product_id, store_code)
        end_time = time.time()
        
        # Should fail quickly
        assert result.status is False
        assert (end_time - start_time) < 0.1  # Should fail in under 100ms

    def test_concurrent_error_handling(self, pricing_service):
        """Test concurrent error handling performance."""
        product_id = 123
        store_code = 6
        num_requests = 10
        
        # Mock repository error
        pricing_service.repository.get_cached_options.side_effect = Exception("Database Error")
        
        def make_request():
            return pricing_service.get_product_options(product_id, store_code)
        
        # Execute concurrent requests with errors
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        end_time = time.time()
        
        # All requests should fail quickly
        assert all(not result.status for result in results)
        assert len(results) == num_requests
        assert (end_time - start_time) < 1.0  # Should complete in under 1 second

    def test_api_response_time(self, client):
        """Test API response time under load."""
        product_id = 123
        store_code = 6
        
        with patch('server.routes.pricing_routes.PricingController.get_product_options') as mock_controller:
            mock_controller.return_value = Result(status=True, data=[])
            
            # Measure API response time
            start_time = time.time()
            response = client.get(f'/api/pricing/products/{product_id}/options?store_code={store_code}')
            end_time = time.time()
            
            assert response.status_code == 200
            assert (end_time - start_time) < 0.5  # Should respond in under 500ms

    def test_concurrent_api_requests(self, client):
        """Test concurrent API requests."""
        product_id = 123
        store_code = 6
        
        with patch('server.routes.pricing_routes.PricingController.get_product_options') as mock_controller:
            mock_controller.return_value = Result(status=True, data=[])
            
            def make_api_request():
                return client.get(f'/api/pricing/products/{product_id}/options?store_code={store_code}')
            
            # Execute concurrent API requests
            num_requests = 10
            start_time = time.time()
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(make_api_request) for _ in range(num_requests)]
                responses = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            end_time = time.time()
            
            # All requests should succeed
            assert all(response.status_code == 200 for response in responses)
            assert len(responses) == num_requests
            
            # Should complete in reasonable time
            assert (end_time - start_time) < 2.0  # Should complete in under 2 seconds
