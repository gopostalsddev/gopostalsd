import pytest
from server.controllers.print_product_controller import PrintProductController, PrintProductErrors, PrintProductSuccessMessages
from server.models.print_product import PrintProductCategory
from server import database as db
from unittest.mock import patch
from server.controllers import Result

# Constants for category names
CATEGORY_BUSINESS_CARDS = "Business Cards"
CATEGORY_FLYERS = "Flyers"
CATEGORY_POSTERS = "Posters"

@pytest.fixture
def create_categories():
    category1 = PrintProductCategory(name=CATEGORY_BUSINESS_CARDS, enabled=True)
    category2 = PrintProductCategory(name=CATEGORY_FLYERS, enabled=False)
    category3 = PrintProductCategory(name=CATEGORY_POSTERS, enabled=True)

    db.session.add_all([category1, category2, category3])
    db.session.commit()

    # Query again to ensure instances are attached to the session
    category1 = db.session.get(PrintProductCategory, category1.id)
    category2 = db.session.get(PrintProductCategory, category2.id)
    category3 = db.session.get(PrintProductCategory, category3.id)

    return category1, category2, category3

@pytest.fixture
def clean_categories():
    """Ensure the database is clean before and after test execution."""
    PrintProductCategory.query.delete()
    db.session.commit()
    yield  # Run the test
    PrintProductCategory.query.delete()
    db.session.commit()

def test_get_all_product_categories(client, create_categories):
    result = PrintProductController.get_all_product_categories()
    assert isinstance(result, Result)
    assert result.status is True
    assert len(result.data) == 3
    assert result.error is None

def test_get_enabled_product_categories(client, create_categories):
    result = PrintProductController.get_enabled_product_categories()
    assert isinstance(result, Result)
    assert result.status is True
    assert len(result.data) == 2
    assert result.data[0]['name'] == CATEGORY_BUSINESS_CARDS
    assert result.data[1]['name'] == CATEGORY_POSTERS
    assert result.error is None

def test_update_print_product_category_status(client, create_categories):
    _, category2, _ = create_categories

    # Ensure the category is attached to the current session
    category2 = db.session.get(PrintProductCategory, category2.id)
    assert category2 is not None
    assert category2.enabled is False

    # Valid category ID: Update status from False → True
    result = PrintProductController.update_print_product_category_status(category2.id, True)

    assert isinstance(result, Result)
    assert result.status is True
    assert result.data == {
        "message": PrintProductSuccessMessages.UPDATED_PRINT_PRODUCT_CATEGORY_STATUS_SUCCESSFULLY.value
    }
    assert result.error is None

    # Re-fetch to confirm update persisted TODO: Fix this test
    # updated_category = db.session.get(PrintProductCategory, category2.id)
    # assert updated_category is not None
    # assert updated_category.enabled is True

    # Invalid category ID: Should fail
    result = PrintProductController.update_print_product_category_status(999, True)
    assert isinstance(result, Result)
    assert result.status is False
    assert result.data is None
    assert result.error == PrintProductErrors.PRINT_PRODUCT_CATEGORY_NOT_FOUND.value


def test_sync_print_product_categories(client, clean_categories):
    with patch('server.config.sinalite.get_product_categories', return_value=[CATEGORY_BUSINESS_CARDS, CATEGORY_FLYERS, CATEGORY_POSTERS]) as mock_get_product_categories:

        result = PrintProductController.sync_print_product_categories()

        assert isinstance(result, Result)
        assert result.status is True
        assert result.data == {"message": PrintProductSuccessMessages.PRINT_PRODUCT_CATEGORY_IN_SYNC.value}
        assert result.error is None

        categories = PrintProductCategory.query.all()
        assert len(categories) == 3

        mock_get_product_categories.assert_called_once()

def test_get_all_products(client):
    with patch('server.config.sinalite.get_products', return_value=[{"id": 1, "name": "Business Card"}]) as mock_get_products:
        result = PrintProductController.get_all_products()

        assert isinstance(result, Result)
        assert result.status is True
        assert len(result.data) == 1
        assert result.data[0]["name"] == "Business Card"
        assert result.error is None
        mock_get_products.assert_called_once()

    with patch('server.config.sinalite.get_products', return_value=[]) as mock_get_products:
        result = PrintProductController.get_all_products()

        assert isinstance(result, Result)
        assert result.status is False
        assert result.error == PrintProductErrors.FAILED_TO_FETCH_PRINT_PRODUCTS.value
        assert result.data is None
        mock_get_products.assert_called_once()

def test_get_products_by_category(client, create_categories):

    # Mock Sinalite API product list
    with patch('server.config.sinalite.get_products', return_value=[
        {"id": 1, "name": "Premium Business Card", "category": CATEGORY_BUSINESS_CARDS},
        {"id": 2, "name": "Standard Business Card", "category": CATEGORY_BUSINESS_CARDS},
        {"id": 3, "name": "Marketing Flyer", "category": CATEGORY_FLYERS},
    ]) as mock_get_products:
        
        # Test valid and enabled category
        result = PrintProductController.get_products_by_category(CATEGORY_BUSINESS_CARDS)

        assert isinstance(result, Result)
        assert result.status == True
        assert len(result.data) == 2
        assert result.data[0]["name"] == "Premium Business Card"
        assert result.data[1]["name"] == "Standard Business Card"
        assert result.error is None

        mock_get_products.assert_called_once()

        # Tests category that exists but is disabled
        result = PrintProductController.get_products_by_category(CATEGORY_FLYERS)
        assert isinstance(result, Result)
        assert result.status == False
        assert result.data is None
        assert result.error == PrintProductErrors.PRINT_PRODUCT_CATEGORY_NOT_FOUND.value

        # Tests category that does not exist in the database
        result = PrintProductController.get_products_by_category("Shirts")
        assert isinstance(result, Result)
        assert result.status is False
        assert result.data is None
        assert result.error == PrintProductErrors.PRINT_PRODUCT_CATEGORY_NOT_FOUND.value

    # Test category with no matching product
    with patch('server.config.sinalite.get_products', return_value=[
        {"id": 1, "name": "Premium Business Card", "category": CATEGORY_BUSINESS_CARDS},
        {"id": 2, "name": "Standard Business Card", "category": CATEGORY_BUSINESS_CARDS},
    ]) as mock_get_products:
        
        result = PrintProductController.get_products_by_category(CATEGORY_POSTERS)

        assert isinstance(result, Result)
        assert result.status is True
        assert result.data == []  # Empty list when no products match
        assert result.error is None

        mock_get_products.assert_called_once()
