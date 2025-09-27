"""
Unit tests for MainFactory.
Tests all methods and edge cases to achieve 100% coverage.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from server.factories.main_factory import MainFactory
from server.factories.repository_factory import RepositoryFactory
from server.factories.service_factory import ServiceFactory
from server.factories.controller_factory import ControllerFactory


class TestMainFactory:
    """Test cases for MainFactory."""

    @pytest.fixture
    def main_factory(self):
        """Create a MainFactory instance for testing."""
        return MainFactory()

    def test_init(self, main_factory):
        """Test factory initialization."""
        assert main_factory is not None
        assert hasattr(main_factory, '_repository_factory')
        assert hasattr(main_factory, '_service_factory')
        assert hasattr(main_factory, '_controller_factory')

    def test_get_pricing_repository(self, main_factory):
        """Test pricing repository retrieval."""
        with patch.object(RepositoryFactory, 'get_pricing_repository') as mock_get:
            mock_repo = Mock()
            mock_get.return_value = mock_repo
            
            result = main_factory.get_pricing_repository()
            
            assert result == mock_repo
            mock_get.assert_called_once()

    def test_get_cart_repository(self, main_factory):
        """Test cart repository retrieval."""
        with patch.object(RepositoryFactory, 'get_cart_repository') as mock_get:
            mock_repo = Mock()
            mock_get.return_value = mock_repo
            
            result = main_factory.get_cart_repository()
            
            assert result == mock_repo
            mock_get.assert_called_once()

    def test_get_pricing_service(self, main_factory):
        """Test pricing service retrieval."""
        with patch.object(ServiceFactory, 'get_pricing_service') as mock_get:
            mock_service = Mock()
            mock_get.return_value = mock_service
            
            result = main_factory.get_pricing_service()
            
            assert result == mock_service
            mock_get.assert_called_once()

    def test_get_cart_service(self, main_factory):
        """Test cart service retrieval."""
        with patch.object(ServiceFactory, 'get_cart_service') as mock_get:
            mock_service = Mock()
            mock_get.return_value = mock_service
            
            result = main_factory.get_cart_service()
            
            assert result == mock_service
            mock_get.assert_called_once()

    def test_get_pricing_controller(self, main_factory):
        """Test pricing controller retrieval."""
        with patch.object(ControllerFactory, 'get_pricing_controller') as mock_get:
            mock_controller = Mock()
            mock_get.return_value = mock_controller
            
            result = main_factory.get_pricing_controller()
            
            assert result == mock_controller
            mock_get.assert_called_once()

    def test_get_print_product_controller(self, main_factory):
        """Test print product controller retrieval."""
        with patch.object(ControllerFactory, 'get_print_product_controller') as mock_get:
            mock_controller = Mock()
            mock_get.return_value = mock_controller
            
            result = main_factory.get_print_product_controller()
            
            assert result == mock_controller
            mock_get.assert_called_once()

    def test_get_user_controller(self, main_factory):
        """Test user controller retrieval."""
        with patch.object(ControllerFactory, 'get_user_controller') as mock_get:
            mock_controller = Mock()
            mock_get.return_value = mock_controller
            
            result = main_factory.get_user_controller()
            
            assert result == mock_controller
            mock_get.assert_called_once()

    def test_reset(self, main_factory):
        """Test factory reset."""
        with patch.object(RepositoryFactory, 'reset') as mock_repo_reset, \
             patch.object(ServiceFactory, 'reset') as mock_service_reset, \
             patch.object(ControllerFactory, 'reset') as mock_controller_reset:
            
            main_factory.reset()
            
            mock_repo_reset.assert_called_once()
            mock_service_reset.assert_called_once()
            mock_controller_reset.assert_called_once()

    def test_singleton_behavior(self):
        """Test that MainFactory follows singleton pattern."""
        factory1 = MainFactory()
        factory2 = MainFactory()
        
        # Should be the same instance
        assert factory1 is factory2

    def test_factory_dependencies(self, main_factory):
        """Test that factory dependencies are properly initialized."""
        assert isinstance(main_factory._repository_factory, RepositoryFactory)
        assert isinstance(main_factory._service_factory, ServiceFactory)
        assert isinstance(main_factory._controller_factory, ControllerFactory)

    def test_get_pricing_repository_caching(self, main_factory):
        """Test that pricing repository is cached."""
        with patch.object(RepositoryFactory, 'get_pricing_repository') as mock_get:
            mock_repo = Mock()
            mock_get.return_value = mock_repo
            
            # Call multiple times
            result1 = main_factory.get_pricing_repository()
            result2 = main_factory.get_pricing_repository()
            
            # Should only be called once due to caching
            assert mock_get.call_count == 1
            assert result1 == result2

    def test_get_cart_repository_caching(self, main_factory):
        """Test that cart repository is cached."""
        with patch.object(RepositoryFactory, 'get_cart_repository') as mock_get:
            mock_repo = Mock()
            mock_get.return_value = mock_repo
            
            # Call multiple times
            result1 = main_factory.get_cart_repository()
            result2 = main_factory.get_cart_repository()
            
            # Should only be called once due to caching
            assert mock_get.call_count == 1
            assert result1 == result2

    def test_get_pricing_service_caching(self, main_factory):
        """Test that pricing service is cached."""
        with patch.object(ServiceFactory, 'get_pricing_service') as mock_get:
            mock_service = Mock()
            mock_get.return_value = mock_service
            
            # Call multiple times
            result1 = main_factory.get_pricing_service()
            result2 = main_factory.get_pricing_service()
            
            # Should only be called once due to caching
            assert mock_get.call_count == 1
            assert result1 == result2

    def test_get_cart_service_caching(self, main_factory):
        """Test that cart service is cached."""
        with patch.object(ServiceFactory, 'get_cart_service') as mock_get:
            mock_service = Mock()
            mock_get.return_value = mock_service
            
            # Call multiple times
            result1 = main_factory.get_cart_service()
            result2 = main_factory.get_cart_service()
            
            # Should only be called once due to caching
            assert mock_get.call_count == 1
            assert result1 == result2

    def test_reset_clears_cache(self, main_factory):
        """Test that reset clears all caches."""
        # First, get some instances to populate cache
        with patch.object(RepositoryFactory, 'get_pricing_repository') as mock_repo_get, \
             patch.object(ServiceFactory, 'get_pricing_service') as mock_service_get:
            
            mock_repo = Mock()
            mock_service = Mock()
            mock_repo_get.return_value = mock_repo
            mock_service_get.return_value = mock_service
            
            main_factory.get_pricing_repository()
            main_factory.get_pricing_service()
            
            # Reset should clear caches
            main_factory.reset()
            
            # Next calls should create new instances
            main_factory.get_pricing_repository()
            main_factory.get_pricing_service()
            
            # Should be called twice (once before reset, once after)
            assert mock_repo_get.call_count == 2
            assert mock_service_get.call_count == 2
