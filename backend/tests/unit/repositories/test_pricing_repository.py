"""
Unit tests for PricingRepository.
Tests all methods and edge cases to achieve 100% coverage.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from server.repositories.pricing_repository import PricingRepository
from server.models.pricing import ProductOption, ProductPricing, ProductVariant
from server.config import database as db


class TestPricingRepository:
    """Test cases for PricingRepository."""

    @pytest.fixture
    def repository(self):
        """Create a PricingRepository instance for testing."""
        return PricingRepository()

    @pytest.fixture
    def sample_options_data(self):
        """Sample options data for testing."""
        return [
            {"id": 5, "group": "qty", "name": "50"},
            {"id": 105, "group": "qty", "name": "25"},
            {"id": 447, "group": "Stock", "name": "Brown Cardboard"}
        ]

    @pytest.fixture
    def sample_pricing_data(self):
        """Sample pricing data for testing."""
        return {
            "price": 22.51,
            "currency": "USD",
            "estimated_ship_date": "2024-01-15"
        }

    def test_init(self, repository):
        """Test repository initialization."""
        assert repository is not None
        assert hasattr(repository, 'get_cached_pricing')
        assert hasattr(repository, 'cache_pricing')
        assert hasattr(repository, 'get_cached_options')
        assert hasattr(repository, 'cache_options')

    def test_cache_options_success(self, app, repository, sample_options_data):
        """Test successful caching of options."""
        product_id = 123
        
        with app.app_context():
            with patch.object(db.session, 'add') as mock_add, \
                 patch.object(db.session, 'commit') as mock_commit, \
                 patch.object(db.session, 'query') as mock_query:
                
                repository.cache_options(product_id, sample_options_data)
                
                mock_add.assert_called()
                mock_commit.assert_called_once()

    def test_cache_options_database_error(self, app, repository, sample_options_data):
        """Test caching options with database error."""
        product_id = 123
        
        with app.app_context():
            with patch.object(db.session, 'add') as mock_add, \
                 patch.object(db.session, 'commit', side_effect=Exception("DB Error")), \
                 patch.object(db.session, 'rollback') as mock_rollback:
                
                repository.cache_options(product_id, sample_options_data)
                
                mock_add.assert_called()
                mock_rollback.assert_called_once()

    def test_cache_variants_success(self, app, repository):
        """Test successful caching of variants."""
        product_id = 123
        variants = [
            {"key": "5-447", "price": 22.51},
            {"key": "10-448", "price": 25.00}
        ]
        
        with app.app_context():
            with patch.object(db.session, 'add_all') as mock_add_all, \
                 patch.object(db.session, 'commit') as mock_commit:
                
                repository.cache_variants(product_id, variants)
                
                mock_add_all.assert_called_once()
                mock_commit.assert_called_once()

    def test_cache_variants_database_error(self, app, repository):
        """Test caching variants with database error."""
        product_id = 123
        variants = [{"key": "5-447", "price": 22.51}]
        
        with app.app_context():
            with patch.object(db.session, 'add_all') as mock_add_all, \
                 patch.object(db.session, 'commit', side_effect=Exception("DB Error")), \
                 patch.object(db.session, 'rollback') as mock_rollback:
                
                repository.cache_variants(product_id, variants)
                
                mock_add_all.assert_called_once()
                mock_rollback.assert_called_once()

    def test_get_cached_options_success(self, app, repository):
        """Test successful retrieval of cached options."""
        product_id = 123
        expected_options = [
            {"id": 5, "group": "qty", "name": "50"},
            {"id": 105, "group": "qty", "name": "25"}
        ]
        
        with app.app_context():
            # Mock the database query
            mock_options = [Mock(id=5, group="qty", name="50"), Mock(id=105, group="qty", name="25")]
            for i, option in enumerate(mock_options):
                option.to_dict.return_value = expected_options[i]
            
            with patch.object(ProductOption, 'query') as mock_query:
                mock_query.filter_by.return_value.all.return_value = mock_options
                
                result = repository.get_cached_options(product_id)
                
                assert result == expected_options
                mock_query.filter_by.assert_called_once_with(product_id=product_id)

    def test_get_cached_options_not_found(self, app, repository):
        """Test retrieval of cached options when none exist."""
        product_id = 123
        
        with app.app_context():
            with patch.object(ProductOption, 'query') as mock_query:
                mock_query.filter_by.return_value.all.return_value = []
                
                result = repository.get_cached_options(product_id)
                
                assert result is None

    def test_get_cached_options_database_error(self, app, repository):
        """Test retrieval of cached options with database error."""
        product_id = 123
        
        with app.app_context():
            with patch.object(ProductOption, 'query') as mock_query:
                mock_query.filter_by.side_effect = Exception("DB Error")
                
                result = repository.get_cached_options(product_id)
                
                assert result is None

    def test_get_cached_pricing_success(self, app, repository):
        """Test successful retrieval of cached pricing."""
        product_id = 123
        store_code = 6
        option_key = "5-447"
        expected_pricing = {"price": 22.51, "currency": "USD"}
        
        with app.app_context():
            # Mock the database query
            mock_pricing = Mock()
            mock_pricing.updated_at = Mock()
            mock_pricing.price = 22.51
            mock_pricing.package_info = "Test package"
            mock_pricing.product_options = "Test options"
            
            with patch.object(ProductPricing, 'query') as mock_query:
                mock_query.filter_by.return_value.first.return_value = mock_pricing
                
                result = repository.get_cached_pricing(product_id, store_code, option_key)
                
                assert result == expected_pricing
                mock_query.filter_by.assert_called_once_with(
                    product_id=product_id, 
                    store_code=store_code,
                    option_key=option_key
                )

    def test_get_cached_pricing_not_found(self, app, repository):
        """Test retrieval of cached pricing when none exists."""
        product_id = 123
        store_code = 6
        option_key = "5-447"
        
        with app.app_context():
            with patch.object(ProductPricing, 'query') as mock_query:
                mock_query.filter_by.return_value.first.return_value = None
                
                result = repository.get_cached_pricing(product_id, store_code, option_key)
                
                assert result is None

    def test_get_cached_pricing_database_error(self, app, repository):
        """Test retrieval of cached pricing with database error."""
        product_id = 123
        store_code = 6
        option_key = "5-447"
        
        with app.app_context():
            with patch.object(ProductPricing, 'query') as mock_query:
                mock_query.filter_by.side_effect = Exception("DB Error")
                
                result = repository.get_cached_pricing(product_id, store_code, option_key)
                
                assert result is None

    def test_cache_pricing_success(self, app, repository):
        """Test successful caching of pricing."""
        product_id = 123
        store_code = 6
        option_key = "5-447"
        pricing_data = {"price": 22.51, "currency": "USD"}
        options = [5, 447]
        
        with app.app_context():
            with patch.object(db.session, 'add') as mock_add, \
                 patch.object(db.session, 'commit') as mock_commit:
                
                repository.cache_pricing(product_id, store_code, option_key, pricing_data, options)
                
                mock_add.assert_called_once()
                mock_commit.assert_called_once()

    def test_cache_pricing_database_error(self, app, repository):
        """Test caching pricing with database error."""
        product_id = 123
        store_code = 6
        option_key = "5-447"
        pricing_data = {"price": 22.51, "currency": "USD"}
        options = [5, 447]
        
        with app.app_context():
            with patch.object(db.session, 'add') as mock_add, \
                 patch.object(db.session, 'commit', side_effect=Exception("DB Error")), \
                 patch.object(db.session, 'rollback') as mock_rollback:
                
                repository.cache_pricing(product_id, store_code, option_key, pricing_data, options)
                
                mock_add.assert_called_once()
                mock_rollback.assert_called_once()
