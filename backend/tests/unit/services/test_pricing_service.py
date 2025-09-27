"""
Unit tests for PricingService.
Tests all methods and edge cases to achieve 100% coverage.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from server.services.pricing_service import PricingService
from server.thirdparty.sinalite import SinaliteAdapter
from server.repositories.pricing_repository import PricingRepository
from server.controllers.helpers import Result


class TestPricingService:
    """Test cases for PricingService."""

    @pytest.fixture
    def mock_sinalite_adapter(self):
        """Create a mock Sinalite adapter."""
        adapter = Mock(spec=SinaliteAdapter)
        adapter.name = "MockSinalite"
        return adapter

    @pytest.fixture
    def mock_repository(self):
        """Create a mock pricing repository."""
        return Mock(spec=PricingRepository)

    @pytest.fixture
    def pricing_service(self, mock_sinalite_adapter, mock_repository):
        """Create a PricingService instance for testing."""
        return PricingService(mock_sinalite_adapter, mock_repository)

    @pytest.fixture
    def sample_product_options(self):
        """Sample product options data."""
        return [
            {
                "group": "qty",
                "options": [
                    {"id": 5, "name": "50"},
                    {"id": 105, "name": "25"}
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
    def sample_pricing_data(self):
        """Sample pricing data."""
        return {
            "price": 22.51,
            "currency": "USD",
            "estimated_ship_date": "2024-01-15"
        }

    def test_init(self, mock_sinalite_adapter, mock_repository):
        """Test service initialization."""
        service = PricingService(mock_sinalite_adapter, mock_repository)
        assert service.sinalite_adapter == mock_sinalite_adapter
        assert service.repository == mock_repository

    def test_get_product_options_success_from_cache(self, pricing_service, sample_product_options):
        """Test successful product options retrieval from cache."""
        product_id = 123
        store_code = 6
        
        # Mock cache hit
        pricing_service.repository.get_cached_options.return_value = sample_product_options
        pricing_service.repository.is_cache_valid.return_value = True
        
        result = pricing_service.get_product_options(product_id, store_code)
        
        assert result.status is True
        assert result.data == sample_product_options
        pricing_service.repository.get_cached_options.assert_called_once_with(product_id, store_code)

    def test_get_product_options_success_from_api(self, pricing_service, sample_product_options):
        """Test successful product options retrieval from API."""
        product_id = 123
        store_code = 6
        
        # Mock cache miss
        pricing_service.repository.get_cached_options.return_value = None
        pricing_service.repository.is_cache_valid.return_value = False
        
        # Mock API call
        pricing_service.sinalite_adapter.get_product_options.return_value = sample_product_options
        
        result = pricing_service.get_product_options(product_id, store_code)
        
        assert result.status is True
        assert result.data == sample_product_options
        pricing_service.sinalite_adapter.get_product_options.assert_called_once_with(product_id, store_code)
        pricing_service.repository.cache_options.assert_called_once_with(product_id, store_code, sample_product_options)

    def test_get_product_options_api_error(self, pricing_service):
        """Test product options retrieval with API error."""
        product_id = 123
        store_code = 6
        
        # Mock cache miss
        pricing_service.repository.get_cached_options.return_value = None
        pricing_service.repository.is_cache_valid.return_value = False
        
        # Mock API error
        pricing_service.sinalite_adapter.get_product_options.side_effect = Exception("API Error")
        
        result = pricing_service.get_product_options(product_id, store_code)
        
        assert result.status is False
        assert "API Error" in result.error

    def test_get_product_options_cache_error(self, pricing_service, sample_product_options):
        """Test product options retrieval with cache error."""
        product_id = 123
        store_code = 6
        
        # Mock cache error
        pricing_service.repository.get_cached_options.side_effect = Exception("Cache Error")
        
        result = pricing_service.get_product_options(product_id, store_code)
        
        assert result.status is False
        assert "Cache Error" in result.error

    def test_calculate_price_success_from_cache(self, pricing_service, sample_pricing_data):
        """Test successful price calculation from cache."""
        product_id = 123
        options = [5, 447]
        store_code = 6
        
        # Mock cache hit
        pricing_service.repository.get_cached_pricing.return_value = sample_pricing_data
        pricing_service.repository.is_cache_valid.return_value = True
        
        result = pricing_service.calculate_price(product_id, options, store_code)
        
        assert result.status is True
        assert result.data == sample_pricing_data

    def test_calculate_price_success_from_api(self, pricing_service, sample_pricing_data):
        """Test successful price calculation from API."""
        product_id = 123
        options = [5, 447]
        store_code = 6
        
        # Mock cache miss
        pricing_service.repository.get_cached_pricing.return_value = None
        pricing_service.repository.is_cache_valid.return_value = False
        
        # Mock API call
        pricing_service.sinalite_adapter.calculate_price.return_value = sample_pricing_data
        
        result = pricing_service.calculate_price(product_id, options, store_code)
        
        assert result.status is True
        assert result.data == sample_pricing_data
        pricing_service.sinalite_adapter.calculate_price.assert_called_once_with(product_id, options, store_code)

    def test_calculate_price_api_error(self, pricing_service):
        """Test price calculation with API error."""
        product_id = 123
        options = [5, 447]
        store_code = 6
        
        # Mock cache miss
        pricing_service.repository.get_cached_pricing.return_value = None
        pricing_service.repository.is_cache_valid.return_value = False
        
        # Mock API error
        pricing_service.sinalite_adapter.calculate_price.side_effect = Exception("API Error")
        
        result = pricing_service.calculate_price(product_id, options, store_code)
        
        assert result.status is False
        assert "API Error" in result.error

    def test_calculate_price_invalid_options(self, pricing_service):
        """Test price calculation with invalid options."""
        product_id = 123
        options = []  # Empty options
        store_code = 6
        
        result = pricing_service.calculate_price(product_id, options, store_code)
        
        assert result.status is False
        assert "No options provided" in result.error

    def test_calculate_price_cache_error(self, pricing_service):
        """Test price calculation with cache error."""
        product_id = 123
        options = [5, 447]
        store_code = 6
        
        # Mock cache error
        pricing_service.repository.get_cached_pricing.side_effect = Exception("Cache Error")
        
        result = pricing_service.calculate_price(product_id, options, store_code)
        
        assert result.status is False
        assert "Cache Error" in result.error

    def test_get_shipping_estimates_success(self, pricing_service, sample_shipping_estimates):
        """Test successful shipping estimates retrieval."""
        items = [{"productId": 123, "options": [5, 447]}]
        shipping_info = {"ShipState": "CA", "ShipZip": "90210", "ShipCountry": "US"}
        
        # Mock API call
        pricing_service.sinalite_adapter.get_shipping_estimates.return_value = sample_shipping_estimates
        
        result = pricing_service.get_shipping_estimates(items, shipping_info)
        
        assert result.status is True
        assert result.data == sample_shipping_estimates
        pricing_service.sinalite_adapter.get_shipping_estimates.assert_called_once_with(items, shipping_info)

    def test_get_shipping_estimates_api_error(self, pricing_service):
        """Test shipping estimates retrieval with API error."""
        items = [{"productId": 123, "options": [5, 447]}]
        shipping_info = {"ShipState": "CA", "ShipZip": "90210", "ShipCountry": "US"}
        
        # Mock API error
        pricing_service.sinalite_adapter.get_shipping_estimates.side_effect = Exception("API Error")
        
        result = pricing_service.get_shipping_estimates(items, shipping_info)
        
        assert result.status is False
        assert "API Error" in result.error

    def test_get_shipping_estimates_invalid_items(self, pricing_service):
        """Test shipping estimates with invalid items."""
        items = []  # Empty items
        shipping_info = {"ShipState": "CA", "ShipZip": "90210", "ShipCountry": "US"}
        
        result = pricing_service.get_shipping_estimates(items, shipping_info)
        
        assert result.status is False
        assert "No items provided" in result.error

    def test_get_shipping_estimates_invalid_shipping_info(self, pricing_service):
        """Test shipping estimates with invalid shipping info."""
        items = [{"productId": 123, "options": [5, 447]}]
        shipping_info = {}  # Empty shipping info
        
        result = pricing_service.get_shipping_estimates(items, shipping_info)
        
        assert result.status is False
        assert "Invalid shipping information" in result.error

    def test_validate_options_success(self, pricing_service):
        """Test successful options validation."""
        options = [5, 447]
        
        result = pricing_service.validate_options(options)
        
        assert result is True

    def test_validate_options_empty(self, pricing_service):
        """Test options validation with empty options."""
        options = []
        
        result = pricing_service.validate_options(options)
        
        assert result is False

    def test_validate_options_invalid_type(self, pricing_service):
        """Test options validation with invalid type."""
        options = "invalid"  # String instead of list
        
        result = pricing_service.validate_options(options)
        
        assert result is False

    def test_validate_shipping_info_success(self, pricing_service):
        """Test successful shipping info validation."""
        shipping_info = {"ShipState": "CA", "ShipZip": "90210", "ShipCountry": "US"}
        
        result = pricing_service.validate_shipping_info(shipping_info)
        
        assert result is True

    def test_validate_shipping_info_missing_fields(self, pricing_service):
        """Test shipping info validation with missing fields."""
        shipping_info = {"ShipState": "CA"}  # Missing required fields
        
        result = pricing_service.validate_shipping_info(shipping_info)
        
        assert result is False

    def test_validate_shipping_info_empty(self, pricing_service):
        """Test shipping info validation with empty info."""
        shipping_info = {}
        
        result = pricing_service.validate_shipping_info(shipping_info)
        
        assert result is False

    def test_clear_cache(self, pricing_service):
        """Test cache clearing."""
        pricing_service.clear_cache()
        
        pricing_service.repository.clear_cache.assert_called_once()

    def test_get_cache_stats(self, pricing_service):
        """Test cache statistics retrieval."""
        expected_stats = {"total_keys": 10, "memory_usage": 1024}
        pricing_service.repository.get_cache_stats.return_value = expected_stats
        
        result = pricing_service.get_cache_stats()
        
        assert result == expected_stats
        pricing_service.repository.get_cache_stats.assert_called_once()
