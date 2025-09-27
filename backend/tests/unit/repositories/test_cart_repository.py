"""
Unit tests for CartRepository.
Tests all methods and edge cases to achieve 100% coverage.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from server.repositories.cart_repository import CartRepository
from server.models.pricing import Cart, CartItem, StoreCode
from server.config import database as db


class TestCartRepository:
    """Test cases for CartRepository."""

    @pytest.fixture
    def repository(self):
        """Create a CartRepository instance for testing."""
        return CartRepository()

    @pytest.fixture
    def sample_cart_data(self):
        """Sample cart data for testing."""
        return {
            "session_id": "test_session_123",
            "user_id": None,
            "store_code": StoreCode.SINALITE
        }

    @pytest.fixture
    def sample_cart_item_data(self):
        """Sample cart item data for testing."""
        return {
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

    def test_init(self, repository):
        """Test repository initialization."""
        assert repository is not None

    def test_get_or_create_cart_new_cart(self, repository, sample_cart_data):
        """Test creating a new cart when none exists."""
        session_id = "new_session"
        user_id = None
        store_code = StoreCode.SINALITE
        
        # Mock the database query to return no existing cart
        with patch.object(Cart, 'query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = None
            
            # Mock the cart creation
            mock_cart = Mock()
            mock_cart.id = 1
            mock_cart.session_id = session_id
            mock_cart.user_id = user_id
            mock_cart.store_code = store_code
            
            with patch.object(db.session, 'add') as mock_add, \
                 patch.object(db.session, 'commit') as mock_commit, \
                 patch('server.repositories.cart_repository.Cart', return_value=mock_cart):
                
                result = repository.get_or_create_cart(session_id, user_id, store_code)
                
                assert result == mock_cart
                mock_add.assert_called_once()
                mock_commit.assert_called_once()

    def test_get_or_create_cart_existing_cart(self, repository, sample_cart_data):
        """Test retrieving an existing cart."""
        session_id = "existing_session"
        user_id = None
        store_code = StoreCode.SINALITE
        
        # Mock the database query to return an existing cart
        mock_cart = Mock()
        mock_cart.id = 1
        mock_cart.session_id = session_id
        mock_cart.user_id = user_id
        mock_cart.store_code = store_code
        
        with patch.object(Cart, 'query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = mock_cart
            
            result = repository.get_or_create_cart(session_id, user_id, store_code)
            
            assert result == mock_cart

    def test_get_or_create_cart_database_error(self, repository, sample_cart_data):
        """Test cart creation/retrieval with database error."""
        session_id = "error_session"
        user_id = None
        store_code = StoreCode.SINALITE
        
        with patch.object(Cart, 'query') as mock_query:
            mock_query.filter_by.side_effect = Exception("DB Error")
            
            result = repository.get_or_create_cart(session_id, user_id, store_code)
            
            assert result is None

    def test_get_cart_by_id_success(self, repository):
        """Test successful cart retrieval by ID."""
        cart_id = 1
        mock_cart = Mock()
        mock_cart.id = cart_id
        
        with patch.object(Cart, 'query') as mock_query:
            mock_query.get.return_value = mock_cart
            
            result = repository.get_cart_by_id(cart_id)
            
            assert result == mock_cart
            mock_query.get.assert_called_once_with(cart_id)

    def test_get_cart_by_id_not_found(self, repository):
        """Test cart retrieval when cart doesn't exist."""
        cart_id = 999
        
        with patch.object(Cart, 'query') as mock_query:
            mock_query.get.return_value = None
            
            result = repository.get_cart_by_id(cart_id)
            
            assert result is None

    def test_get_cart_by_id_database_error(self, repository):
        """Test cart retrieval with database error."""
        cart_id = 1
        
        with patch.object(Cart, 'query') as mock_query:
            mock_query.get.side_effect = Exception("DB Error")
            
            result = repository.get_cart_by_id(cart_id)
            
            assert result is None

    def test_add_cart_item_success(self, repository, sample_cart_item_data):
        """Test successful cart item addition."""
        mock_cart_item = Mock()
        mock_cart_item.id = 1
        
        with patch.object(db.session, 'add') as mock_add, \
             patch.object(db.session, 'commit') as mock_commit, \
             patch('server.repositories.cart_repository.CartItem', return_value=mock_cart_item):
            
            result = repository.add_cart_item(**sample_cart_item_data)
            
            assert result == mock_cart_item
            mock_add.assert_called_once()
            mock_commit.assert_called_once()

    def test_add_cart_item_database_error(self, repository, sample_cart_item_data):
        """Test cart item addition with database error."""
        with patch.object(db.session, 'add') as mock_add, \
             patch.object(db.session, 'commit', side_effect=Exception("DB Error")), \
             patch.object(db.session, 'rollback') as mock_rollback:
            
            result = repository.add_cart_item(**sample_cart_item_data)
            
            assert result is None
            mock_rollback.assert_called_once()

    def test_update_cart_item_success(self, repository):
        """Test successful cart item update."""
        item_id = 1
        update_data = {"quantity": 5, "total_price": 50.00}
        
        mock_item = Mock()
        mock_item.id = item_id
        
        with patch.object(CartItem, 'query') as mock_query, \
             patch.object(db.session, 'commit') as mock_commit:
            mock_query.get.return_value = mock_item
            
            result = repository.update_cart_item(item_id, update_data)
            
            assert result == mock_item
            mock_commit.assert_called_once()

    def test_update_cart_item_not_found(self, repository):
        """Test cart item update when item doesn't exist."""
        item_id = 999
        update_data = {"quantity": 5}
        
        with patch.object(CartItem, 'query') as mock_query:
            mock_query.get.return_value = None
            
            result = repository.update_cart_item(item_id, update_data)
            
            assert result is None

    def test_update_cart_item_database_error(self, repository):
        """Test cart item update with database error."""
        item_id = 1
        update_data = {"quantity": 5}
        
        with patch.object(CartItem, 'query') as mock_query, \
             patch.object(db.session, 'commit', side_effect=Exception("DB Error")), \
             patch.object(db.session, 'rollback') as mock_rollback:
            mock_query.get.return_value = Mock()
            
            result = repository.update_cart_item(item_id, update_data)
            
            assert result is None
            mock_rollback.assert_called_once()

    def test_get_cart_item_by_id_success(self, repository):
        """Test successful cart item retrieval by ID."""
        item_id = 1
        mock_item = Mock()
        mock_item.id = item_id
        
        with patch.object(CartItem, 'query') as mock_query:
            mock_query.get.return_value = mock_item
            
            result = repository.get_cart_item_by_id(item_id)
            
            assert result == mock_item
            mock_query.get.assert_called_once_with(item_id)

    def test_get_cart_item_by_id_not_found(self, repository):
        """Test cart item retrieval when item doesn't exist."""
        item_id = 999
        
        with patch.object(CartItem, 'query') as mock_query:
            mock_query.get.return_value = None
            
            result = repository.get_cart_item_by_id(item_id)
            
            assert result is None

    def test_get_cart_item_by_id_database_error(self, repository):
        """Test cart item retrieval with database error."""
        item_id = 1
        
        with patch.object(CartItem, 'query') as mock_query:
            mock_query.get.side_effect = Exception("DB Error")
            
            result = repository.get_cart_item_by_id(item_id)
            
            assert result is None

    def test_get_cart_items_success(self, repository):
        """Test successful cart items retrieval."""
        cart_id = 1
        mock_items = [Mock(id=1), Mock(id=2)]
        
        with patch.object(CartItem, 'query') as mock_query:
            mock_query.filter_by.return_value.all.return_value = mock_items
            
            result = repository.get_cart_items(cart_id)
            
            assert result == mock_items
            mock_query.filter_by.assert_called_once_with(cart_id=cart_id)

    def test_get_cart_items_empty(self, repository):
        """Test cart items retrieval when cart is empty."""
        cart_id = 1
        
        with patch.object(CartItem, 'query') as mock_query:
            mock_query.filter_by.return_value.all.return_value = []
            
            result = repository.get_cart_items(cart_id)
            
            assert result == []

    def test_get_cart_items_database_error(self, repository):
        """Test cart items retrieval with database error."""
        cart_id = 1
        
        with patch.object(CartItem, 'query') as mock_query:
            mock_query.filter_by.side_effect = Exception("DB Error")
            
            result = repository.get_cart_items(cart_id)
            
            assert result is None

    def test_delete_cart_item_success(self, repository):
        """Test successful cart item deletion."""
        item_id = 1
        mock_item = Mock()
        mock_item.id = item_id
        
        with patch.object(CartItem, 'query') as mock_query, \
             patch.object(db.session, 'delete') as mock_delete, \
             patch.object(db.session, 'commit') as mock_commit:
            mock_query.get.return_value = mock_item
            
            result = repository.delete_cart_item(item_id)
            
            assert result is True
            mock_delete.assert_called_once_with(mock_item)
            mock_commit.assert_called_once()

    def test_delete_cart_item_not_found(self, repository):
        """Test cart item deletion when item doesn't exist."""
        item_id = 999
        
        with patch.object(CartItem, 'query') as mock_query:
            mock_query.get.return_value = None
            
            result = repository.delete_cart_item(item_id)
            
            assert result is False

    def test_delete_cart_item_database_error(self, repository):
        """Test cart item deletion with database error."""
        item_id = 1
        
        with patch.object(CartItem, 'query') as mock_query, \
             patch.object(db.session, 'delete') as mock_delete, \
             patch.object(db.session, 'commit', side_effect=Exception("DB Error")), \
             patch.object(db.session, 'rollback') as mock_rollback:
            mock_query.get.return_value = Mock()
            
            result = repository.delete_cart_item(item_id)
            
            assert result is False
            mock_rollback.assert_called_once()
