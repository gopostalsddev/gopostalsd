"""
Unit tests for CartService.
Tests all methods and edge cases to achieve 100% coverage.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from server.services.cart_service import CartService
from server.services.pricing_service import PricingService
from server.repositories.cart_repository import CartRepository
from server.models.pricing import StoreCode
from server.controllers.helpers import Result


class TestCartService:
    """Test cases for CartService."""

    @pytest.fixture
    def mock_pricing_service(self):
        """Create a mock pricing service."""
        return Mock(spec=PricingService)

    @pytest.fixture
    def mock_repository(self):
        """Create a mock cart repository."""
        return Mock(spec=CartRepository)

    @pytest.fixture
    def cart_service(self, mock_pricing_service, mock_repository):
        """Create a CartService instance for testing."""
        return CartService(mock_pricing_service, mock_repository)

    @pytest.fixture
    def sample_cart_data(self):
        """Sample cart data."""
        return {
            "id": 1,
            "session_id": "test_session_123",
            "user_id": None,
            "store_code": StoreCode.SINALITE,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }

    @pytest.fixture
    def sample_cart_item_data(self):
        """Sample cart item data."""
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

    def test_init(self, mock_pricing_service, mock_repository):
        """Test service initialization."""
        service = CartService(mock_pricing_service, mock_repository)
        assert service.pricing_service == mock_pricing_service
        assert service.repository == mock_repository

    def test_get_or_create_cart_success(self, cart_service, sample_cart_data):
        """Test successful cart creation/retrieval."""
        session_id = "test_session"
        user_id = None
        store_code = StoreCode.SINALITE
        
        # Mock repository call
        mock_cart = Mock()
        mock_cart.to_dict.return_value = sample_cart_data
        cart_service.repository.get_or_create_cart.return_value = mock_cart
        
        result = cart_service.get_or_create_cart(session_id, user_id, store_code)
        
        assert result.status is True
        assert result.data == sample_cart_data
        cart_service.repository.get_or_create_cart.assert_called_once_with(session_id, user_id, store_code)

    def test_get_or_create_cart_repository_error(self, cart_service):
        """Test cart creation/retrieval with repository error."""
        session_id = "test_session"
        user_id = None
        store_code = StoreCode.SINALITE
        
        # Mock repository error
        cart_service.repository.get_or_create_cart.side_effect = Exception("Repository Error")
        
        result = cart_service.get_or_create_cart(session_id, user_id, store_code)
        
        assert result.status is False
        assert "Repository Error" in result.error

    def test_add_item_to_cart_success(self, cart_service, sample_cart_item_data):
        """Test successful cart item addition."""
        cart_id = 1
        product_id = 123
        product_name = "Test Product"
        product_sku = "TEST-001"
        quantity = 2
        selected_options = [5, 447]
        
        # Mock pricing service call
        mock_pricing_result = Mock()
        mock_pricing_result.status = True
        mock_pricing_result.data = {"price": 10.50}
        cart_service.pricing_service.calculate_price.return_value = mock_pricing_result
        
        # Mock repository call
        mock_cart_item = Mock()
        mock_cart_item.to_dict.return_value = sample_cart_item_data
        cart_service.repository.add_cart_item.return_value = mock_cart_item
        
        result = cart_service.add_item_to_cart(
            cart_id, product_id, product_name, product_sku, 
            quantity, selected_options
        )
        
        assert result.status is True
        assert result.data == sample_cart_item_data
        cart_service.pricing_service.calculate_price.assert_called_once_with(
            product_id, selected_options, StoreCode.SINALITE
        )
        cart_service.repository.add_cart_item.assert_called_once()

    def test_add_item_to_cart_pricing_error(self, cart_service):
        """Test cart item addition with pricing error."""
        cart_id = 1
        product_id = 123
        product_name = "Test Product"
        product_sku = "TEST-001"
        quantity = 2
        selected_options = [5, 447]
        
        # Mock pricing service error
        mock_pricing_result = Mock()
        mock_pricing_result.status = False
        mock_pricing_result.error = "Pricing Error"
        cart_service.pricing_service.calculate_price.return_value = mock_pricing_result
        
        result = cart_service.add_item_to_cart(
            cart_id, product_id, product_name, product_sku, 
            quantity, selected_options
        )
        
        assert result.status is False
        assert "Pricing Error" in result.error

    def test_add_item_to_cart_repository_error(self, cart_service):
        """Test cart item addition with repository error."""
        cart_id = 1
        product_id = 123
        product_name = "Test Product"
        product_sku = "TEST-001"
        quantity = 2
        selected_options = [5, 447]
        
        # Mock pricing service success
        mock_pricing_result = Mock()
        mock_pricing_result.status = True
        mock_pricing_result.data = {"price": 10.50}
        cart_service.pricing_service.calculate_price.return_value = mock_pricing_result
        
        # Mock repository error
        cart_service.repository.add_cart_item.side_effect = Exception("Repository Error")
        
        result = cart_service.add_item_to_cart(
            cart_id, product_id, product_name, product_sku, 
            quantity, selected_options
        )
        
        assert result.status is False
        assert "Repository Error" in result.error

    def test_add_item_to_cart_invalid_quantity(self, cart_service):
        """Test cart item addition with invalid quantity."""
        cart_id = 1
        product_id = 123
        product_name = "Test Product"
        product_sku = "TEST-001"
        quantity = 0  # Invalid quantity
        selected_options = [5, 447]
        
        result = cart_service.add_item_to_cart(
            cart_id, product_id, product_name, product_sku, 
            quantity, selected_options
        )
        
        assert result.status is False
        assert "Invalid quantity" in result.error

    def test_add_item_to_cart_invalid_options(self, cart_service):
        """Test cart item addition with invalid options."""
        cart_id = 1
        product_id = 123
        product_name = "Test Product"
        product_sku = "TEST-001"
        quantity = 2
        selected_options = []  # Invalid options
        
        result = cart_service.add_item_to_cart(
            cart_id, product_id, product_name, product_sku, 
            quantity, selected_options
        )
        
        assert result.status is False
        assert "Invalid options" in result.error

    def test_update_cart_item_quantity_success(self, cart_service, sample_cart_item_data):
        """Test successful cart item quantity update."""
        item_id = 1
        new_quantity = 5
        
        # Mock repository calls
        mock_item = Mock()
        mock_item.to_dict.return_value = sample_cart_item_data
        cart_service.repository.get_cart_item_by_id.return_value = mock_item
        cart_service.repository.update_cart_item.return_value = mock_item
        
        result = cart_service.update_cart_item_quantity(item_id, new_quantity)
        
        assert result.status is True
        assert result.data == sample_cart_item_data
        cart_service.repository.get_cart_item_by_id.assert_called_once_with(item_id)
        cart_service.repository.update_cart_item.assert_called_once()

    def test_update_cart_item_quantity_item_not_found(self, cart_service):
        """Test cart item quantity update when item doesn't exist."""
        item_id = 999
        new_quantity = 5
        
        # Mock repository call
        cart_service.repository.get_cart_item_by_id.return_value = None
        
        result = cart_service.update_cart_item_quantity(item_id, new_quantity)
        
        assert result.status is False
        assert "Cart item not found" in result.error

    def test_update_cart_item_quantity_invalid_quantity(self, cart_service):
        """Test cart item quantity update with invalid quantity."""
        item_id = 1
        new_quantity = 0  # Invalid quantity
        
        result = cart_service.update_cart_item_quantity(item_id, new_quantity)
        
        assert result.status is False
        assert "Invalid quantity" in result.error

    def test_update_cart_item_quantity_repository_error(self, cart_service):
        """Test cart item quantity update with repository error."""
        item_id = 1
        new_quantity = 5
        
        # Mock repository error
        cart_service.repository.get_cart_item_by_id.side_effect = Exception("Repository Error")
        
        result = cart_service.update_cart_item_quantity(item_id, new_quantity)
        
        assert result.status is False
        assert "Repository Error" in result.error

    def test_remove_cart_item_success(self, cart_service):
        """Test successful cart item removal."""
        item_id = 1
        
        # Mock repository call
        cart_service.repository.delete_cart_item.return_value = True
        
        result = cart_service.remove_cart_item(item_id)
        
        assert result.status is True
        cart_service.repository.delete_cart_item.assert_called_once_with(item_id)

    def test_remove_cart_item_not_found(self, cart_service):
        """Test cart item removal when item doesn't exist."""
        item_id = 999
        
        # Mock repository call
        cart_service.repository.delete_cart_item.return_value = False
        
        result = cart_service.remove_cart_item(item_id)
        
        assert result.status is False
        assert "Cart item not found" in result.error

    def test_remove_cart_item_repository_error(self, cart_service):
        """Test cart item removal with repository error."""
        item_id = 1
        
        # Mock repository error
        cart_service.repository.delete_cart_item.side_effect = Exception("Repository Error")
        
        result = cart_service.remove_cart_item(item_id)
        
        assert result.status is False
        assert "Repository Error" in result.error

    def test_get_cart_total_success(self, cart_service, sample_cart_item_data):
        """Test successful cart total calculation."""
        cart_id = 1
        
        # Mock repository call
        mock_items = [Mock(), Mock()]
        mock_items[0].to_dict.return_value = sample_cart_item_data
        mock_items[1].to_dict.return_value = {**sample_cart_item_data, "total_price": 15.00}
        cart_service.repository.get_cart_items.return_value = mock_items
        
        result = cart_service.get_cart_total(cart_id)
        
        assert result.status is True
        assert result.data["total_items"] == 2
        assert result.data["total_price"] == 36.00  # 21.00 + 15.00
        cart_service.repository.get_cart_items.assert_called_once_with(cart_id)

    def test_get_cart_total_empty_cart(self, cart_service):
        """Test cart total calculation for empty cart."""
        cart_id = 1
        
        # Mock repository call
        cart_service.repository.get_cart_items.return_value = []
        
        result = cart_service.get_cart_total(cart_id)
        
        assert result.status is True
        assert result.data["total_items"] == 0
        assert result.data["total_price"] == 0.0

    def test_get_cart_total_repository_error(self, cart_service):
        """Test cart total calculation with repository error."""
        cart_id = 1
        
        # Mock repository error
        cart_service.repository.get_cart_items.side_effect = Exception("Repository Error")
        
        result = cart_service.get_cart_total(cart_id)
        
        assert result.status is False
        assert "Repository Error" in result.error

    def test_validate_quantity_success(self, cart_service):
        """Test successful quantity validation."""
        quantity = 5
        
        result = cart_service.validate_quantity(quantity)
        
        assert result is True

    def test_validate_quantity_invalid(self, cart_service):
        """Test quantity validation with invalid values."""
        invalid_quantities = [0, -1, "invalid", None]
        
        for quantity in invalid_quantities:
            result = cart_service.validate_quantity(quantity)
            assert result is False

    def test_validate_options_success(self, cart_service):
        """Test successful options validation."""
        options = [5, 447]
        
        result = cart_service.validate_options(options)
        
        assert result is True

    def test_validate_options_invalid(self, cart_service):
        """Test options validation with invalid values."""
        invalid_options = [[], None, "invalid"]
        
        for options in invalid_options:
            result = cart_service.validate_options(options)
            assert result is False

    def test_calculate_item_total_success(self, cart_service):
        """Test successful item total calculation."""
        unit_price = 10.50
        quantity = 2
        
        result = cart_service.calculate_item_total(unit_price, quantity)
        
        assert result == 21.00

    def test_calculate_item_total_edge_cases(self, cart_service):
        """Test item total calculation with edge cases."""
        # Test with zero price
        assert cart_service.calculate_item_total(0, 5) == 0.0
        
        # Test with zero quantity
        assert cart_service.calculate_item_total(10.50, 0) == 0.0
        
        # Test with decimal values
        assert cart_service.calculate_item_total(10.555, 2) == 21.11
