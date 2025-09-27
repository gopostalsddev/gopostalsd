"""
Unit tests for PricingController.
Tests all methods and edge cases to achieve 100% coverage.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from server.controllers.pricing_controller import PricingController
from server.controllers.helpers import Result


class TestPricingController:
    """Test cases for PricingController."""

    @pytest.fixture
    def mock_pricing_service(self):
        """Create a mock pricing service."""
        return Mock()

    @pytest.fixture
    def mock_cart_service(self):
        """Create a mock cart service."""
        return Mock()

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

    @pytest.fixture
    def sample_cart_data(self):
        """Sample cart data."""
        return {
            "id": 1,
            "session_id": "test_session_123",
            "user_id": None,
            "store_code": 6
        }

    @pytest.fixture
    def sample_cart_item_data(self):
        """Sample cart item data."""
        return {
            "id": 1,
            "cart_id": 1,
            "product_id": 123,
            "product_name": "Test Product",
            "quantity": 2,
            "total_price": 21.00
        }

    def test_get_product_options_success(self, mock_pricing_service, sample_product_options):
        """Test successful product options retrieval."""
        product_id = 123
        store_code = 6
        
        # Mock service call
        mock_result = Result(status=True, data=sample_product_options)
        mock_pricing_service.get_product_options.return_value = mock_result
        
        result = PricingController.get_product_options(product_id, store_code, mock_pricing_service)
        
        assert result.status is True
        assert result.data == sample_product_options
        mock_pricing_service.get_product_options.assert_called_once_with(product_id, store_code)

    def test_get_product_options_service_error(self, mock_pricing_service):
        """Test product options retrieval with service error."""
        product_id = 123
        store_code = 6
        
        # Mock service error
        mock_result = Result(status=False, error="Service Error")
        mock_pricing_service.get_product_options.return_value = mock_result
        
        result = PricingController.get_product_options(product_id, store_code, mock_pricing_service)
        
        assert result.status is False
        assert result.error == "Service Error"

    def test_get_product_options_invalid_parameters(self, mock_pricing_service):
        """Test product options retrieval with invalid parameters."""
        # Test with None product_id
        result = PricingController.get_product_options(None, 6, mock_pricing_service)
        assert result.status is False
        assert "Invalid product ID" in result.error
        
        # Test with None store_code
        result = PricingController.get_product_options(123, None, mock_pricing_service)
        assert result.status is False
        assert "Invalid store code" in result.error

    def test_calculate_price_success(self, mock_pricing_service, sample_pricing_data):
        """Test successful price calculation."""
        product_id = 123
        options = [5, 447]
        store_code = 6
        
        # Mock service call
        mock_result = Result(status=True, data=sample_pricing_data)
        mock_pricing_service.calculate_price.return_value = mock_result
        
        result = PricingController.calculate_price(product_id, options, store_code, mock_pricing_service)
        
        assert result.status is True
        assert result.data == sample_pricing_data
        mock_pricing_service.calculate_price.assert_called_once_with(product_id, options, store_code)

    def test_calculate_price_service_error(self, mock_pricing_service):
        """Test price calculation with service error."""
        product_id = 123
        options = [5, 447]
        store_code = 6
        
        # Mock service error
        mock_result = Result(status=False, error="Service Error")
        mock_pricing_service.calculate_price.return_value = mock_result
        
        result = PricingController.calculate_price(product_id, options, store_code, mock_pricing_service)
        
        assert result.status is False
        assert result.error == "Service Error"

    def test_calculate_price_invalid_parameters(self, mock_pricing_service):
        """Test price calculation with invalid parameters."""
        # Test with None product_id
        result = PricingController.calculate_price(None, [5, 447], 6, mock_pricing_service)
        assert result.status is False
        assert "Invalid product ID" in result.error
        
        # Test with empty options
        result = PricingController.calculate_price(123, [], 6, mock_pricing_service)
        assert result.status is False
        assert "Invalid options" in result.error

    def test_get_cart_totals_success(self, mock_cart_service):
        """Test successful cart totals retrieval."""
        cart_id = 1
        expected_totals = {"total_items": 2, "total_price": 42.00}
        
        # Mock service call
        mock_result = Result(status=True, data=expected_totals)
        mock_cart_service.get_cart_total.return_value = mock_result
        
        result = PricingController.get_cart_totals(cart_id, mock_cart_service)
        
        assert result.status is True
        assert result.data == expected_totals
        mock_cart_service.get_cart_total.assert_called_once_with(cart_id)

    def test_get_cart_totals_service_error(self, mock_cart_service):
        """Test cart totals retrieval with service error."""
        cart_id = 1
        
        # Mock service error
        mock_result = Result(status=False, error="Service Error")
        mock_cart_service.get_cart_total.return_value = mock_result
        
        result = PricingController.get_cart_totals(cart_id, mock_cart_service)
        
        assert result.status is False
        assert result.error == "Service Error"

    def test_get_cart_totals_invalid_parameters(self, mock_cart_service):
        """Test cart totals retrieval with invalid parameters."""
        # Test with None cart_id
        result = PricingController.get_cart_totals(None, mock_cart_service)
        assert result.status is False
        assert "Invalid cart ID" in result.error

    def test_get_shipping_estimates_success(self, mock_pricing_service):
        """Test successful shipping estimates retrieval."""
        items = [{"productId": 123, "options": [5, 447]}]
        shipping_info = {"ShipState": "CA", "ShipZip": "90210", "ShipCountry": "US"}
        expected_estimates = [
            ["UPS", "UPS Standard", 9.1, 1],
            ["FedEx", "FedEx Standard Overnight", 9.67, 1]
        ]
        
        # Mock service call
        mock_result = Result(status=True, data=expected_estimates)
        mock_pricing_service.get_shipping_estimates.return_value = mock_result
        
        result = PricingController.get_shipping_estimates(items, shipping_info, mock_pricing_service)
        
        assert result.status is True
        assert result.data == expected_estimates
        mock_pricing_service.get_shipping_estimates.assert_called_once_with(items, shipping_info)

    def test_get_shipping_estimates_service_error(self, mock_pricing_service):
        """Test shipping estimates retrieval with service error."""
        items = [{"productId": 123, "options": [5, 447]}]
        shipping_info = {"ShipState": "CA", "ShipZip": "90210", "ShipCountry": "US"}
        
        # Mock service error
        mock_result = Result(status=False, error="Service Error")
        mock_pricing_service.get_shipping_estimates.return_value = mock_result
        
        result = PricingController.get_shipping_estimates(items, shipping_info, mock_pricing_service)
        
        assert result.status is False
        assert result.error == "Service Error"

    def test_get_shipping_estimates_invalid_parameters(self, mock_pricing_service):
        """Test shipping estimates retrieval with invalid parameters."""
        # Test with None items
        result = PricingController.get_shipping_estimates(None, {}, mock_pricing_service)
        assert result.status is False
        assert "Invalid items" in result.error
        
        # Test with None shipping_info
        result = PricingController.get_shipping_estimates([], None, mock_pricing_service)
        assert result.status is False
        assert "Invalid shipping information" in result.error

    def test_get_or_create_cart_success(self, mock_cart_service, sample_cart_data):
        """Test successful cart creation/retrieval."""
        session_id = "test_session"
        user_id = None
        store_code = 6
        
        # Mock service call
        mock_result = Result(status=True, data=sample_cart_data)
        mock_cart_service.get_or_create_cart.return_value = mock_result
        
        result = PricingController.get_or_create_cart(session_id, user_id, store_code, mock_cart_service)
        
        assert result.status is True
        assert result.data == sample_cart_data
        mock_cart_service.get_or_create_cart.assert_called_once_with(session_id, user_id, store_code)

    def test_get_or_create_cart_service_error(self, mock_cart_service):
        """Test cart creation/retrieval with service error."""
        session_id = "test_session"
        user_id = None
        store_code = 6
        
        # Mock service error
        mock_result = Result(status=False, error="Service Error")
        mock_cart_service.get_or_create_cart.return_value = mock_result
        
        result = PricingController.get_or_create_cart(session_id, user_id, store_code, mock_cart_service)
        
        assert result.status is False
        assert result.error == "Service Error"

    def test_get_or_create_cart_invalid_parameters(self, mock_cart_service):
        """Test cart creation/retrieval with invalid parameters."""
        # Test with None session_id
        result = PricingController.get_or_create_cart(None, None, 6, mock_cart_service)
        assert result.status is False
        assert "Invalid session ID" in result.error

    def test_add_item_to_cart_success(self, mock_cart_service, sample_cart_item_data):
        """Test successful cart item addition."""
        cart_id = 1
        product_id = 123
        product_name = "Test Product"
        product_sku = "TEST-001"
        quantity = 2
        selected_options = [5, 447]
        
        # Mock service call
        mock_result = Result(status=True, data=sample_cart_item_data)
        mock_cart_service.add_item_to_cart.return_value = mock_result
        
        result = PricingController.add_item_to_cart(
            cart_id, product_id, product_name, product_sku, 
            quantity, selected_options, mock_cart_service
        )
        
        assert result.status is True
        assert result.data == sample_cart_item_data
        mock_cart_service.add_item_to_cart.assert_called_once_with(
            cart_id, product_id, product_name, product_sku, 
            quantity, selected_options
        )

    def test_add_item_to_cart_service_error(self, mock_cart_service):
        """Test cart item addition with service error."""
        cart_id = 1
        product_id = 123
        product_name = "Test Product"
        product_sku = "TEST-001"
        quantity = 2
        selected_options = [5, 447]
        
        # Mock service error
        mock_result = Result(status=False, error="Service Error")
        mock_cart_service.add_item_to_cart.return_value = mock_result
        
        result = PricingController.add_item_to_cart(
            cart_id, product_id, product_name, product_sku, 
            quantity, selected_options, mock_cart_service
        )
        
        assert result.status is False
        assert result.error == "Service Error"

    def test_add_item_to_cart_invalid_parameters(self, mock_cart_service):
        """Test cart item addition with invalid parameters."""
        # Test with None cart_id
        result = PricingController.add_item_to_cart(
            None, 123, "Test Product", "TEST-001", 2, [5, 447], mock_cart_service
        )
        assert result.status is False
        assert "Invalid cart ID" in result.error
        
        # Test with None product_id
        result = PricingController.add_item_to_cart(
            1, None, "Test Product", "TEST-001", 2, [5, 447], mock_cart_service
        )
        assert result.status is False
        assert "Invalid product ID" in result.error

    def test_validate_product_id_success(self):
        """Test successful product ID validation."""
        valid_ids = [123, 456, 789]
        
        for product_id in valid_ids:
            result = PricingController.validate_product_id(product_id)
            assert result is True

    def test_validate_product_id_invalid(self):
        """Test product ID validation with invalid values."""
        invalid_ids = [None, 0, -1, "invalid", []]
        
        for product_id in invalid_ids:
            result = PricingController.validate_product_id(product_id)
            assert result is False

    def test_validate_store_code_success(self):
        """Test successful store code validation."""
        valid_codes = [6, 1, 2]
        
        for store_code in valid_codes:
            result = PricingController.validate_store_code(store_code)
            assert result is True

    def test_validate_store_code_invalid(self):
        """Test store code validation with invalid values."""
        invalid_codes = [None, 0, -1, "invalid", []]
        
        for store_code in invalid_codes:
            result = PricingController.validate_store_code(store_code)
            assert result is False

    def test_validate_options_success(self):
        """Test successful options validation."""
        valid_options = [[5, 447], [1, 2, 3], [100]]
        
        for options in valid_options:
            result = PricingController.validate_options(options)
            assert result is True

    def test_validate_options_invalid(self):
        """Test options validation with invalid values."""
        invalid_options = [None, [], "invalid", 123]
        
        for options in invalid_options:
            result = PricingController.validate_options(options)
            assert result is False

    def test_validate_cart_id_success(self):
        """Test successful cart ID validation."""
        valid_ids = [1, 123, 456]
        
        for cart_id in valid_ids:
            result = PricingController.validate_cart_id(cart_id)
            assert result is True

    def test_validate_cart_id_invalid(self):
        """Test cart ID validation with invalid values."""
        invalid_ids = [None, 0, -1, "invalid", []]
        
        for cart_id in invalid_ids:
            result = PricingController.validate_cart_id(cart_id)
            assert result is False

    def test_validate_session_id_success(self):
        """Test successful session ID validation."""
        valid_ids = ["session_123", "test_session", "abc123"]
        
        for session_id in valid_ids:
            result = PricingController.validate_session_id(session_id)
            assert result is True

    def test_validate_session_id_invalid(self):
        """Test session ID validation with invalid values."""
        invalid_ids = [None, "", "   ", 123, []]
        
        for session_id in invalid_ids:
            result = PricingController.validate_session_id(session_id)
            assert result is False

    def test_validate_items_success(self):
        """Test successful items validation."""
        valid_items = [
            [{"productId": 123, "options": [5, 447]}],
            [{"productId": 1, "options": [1]}, {"productId": 2, "options": [2]}]
        ]
        
        for items in valid_items:
            result = PricingController.validate_items(items)
            assert result is True

    def test_validate_items_invalid(self):
        """Test items validation with invalid values."""
        invalid_items = [None, [], "invalid", 123]
        
        for items in invalid_items:
            result = PricingController.validate_items(items)
            assert result is False

    def test_validate_shipping_info_success(self):
        """Test successful shipping info validation."""
        valid_info = {
            "ShipState": "CA",
            "ShipZip": "90210",
            "ShipCountry": "US"
        }
        
        result = PricingController.validate_shipping_info(valid_info)
        assert result is True

    def test_validate_shipping_info_invalid(self):
        """Test shipping info validation with invalid values."""
        invalid_info = [None, {}, "invalid", 123]
        
        for info in invalid_info:
            result = PricingController.validate_shipping_info(info)
            assert result is False
