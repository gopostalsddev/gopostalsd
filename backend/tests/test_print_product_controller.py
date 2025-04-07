import pytest
from server.controllers.print_product_controller import (
    PrintProductController,
    PrintProductErrors,
    PrintProductSuccessMessages
)
from server.models.print_product import PrintProductCategory
from server import database as db
from unittest.mock import patch
from server.controllers import Result

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

    # Re-attach for access to IDs
    return (
        db.session.get(PrintProductCategory, category1.id),
        db.session.get(PrintProductCategory, category2.id),
        db.session.get(PrintProductCategory, category3.id),
    )

@pytest.fixture
def clean_categories():
    PrintProductCategory.query.delete()
    db.session.commit()
    yield
    PrintProductCategory.query.delete()
    db.session.commit()

# ========== EMPTY TABLE COVERAGE ==========

def test_get_all_product_categories_empty(client, clean_categories):
    result = PrintProductController.get_all_product_categories()
    assert isinstance(result, Result)
    assert result.status is True
    assert result.data == []
    assert result.error is None

def test_get_enabled_product_categories_empty(client, clean_categories):
    result = PrintProductController.get_enabled_product_categories()
    assert isinstance(result, Result)
    assert result.status is True
    assert result.data == []
    assert result.error is None

def test_update_print_product_category_status_empty(client, clean_categories):
    result = PrintProductController.update_print_product_category_status(1, True)
    assert isinstance(result, Result)
    assert result.status is True  # Still true, just returns empty list
    assert result.data == []
    assert result.error is None

def test_get_products_by_category_empty(client, clean_categories):
    result = PrintProductController.get_products_by_category(CATEGORY_BUSINESS_CARDS)
    assert isinstance(result, Result)
    assert result.status is True
    assert result.data == []
    assert result.error is None

# ========== STANDARD TESTS ==========

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
    assert result.error is None

def test_update_print_product_category_status(client, create_categories):
    _, category2, _ = create_categories
    assert category2.enabled is False

    result = PrintProductController.update_print_product_category_status(category2.id, True)
    assert result.status is True
    assert result.data == {
        "message": PrintProductSuccessMessages.UPDATED_PRINT_PRODUCT_CATEGORY_STATUS_SUCCESSFULLY.value
    }

    # Confirm DB updated
    updated = db.session.get(PrintProductCategory, category2.id)
    assert updated.enabled is True

    result = PrintProductController.update_print_product_category_status(9999, False)
    assert result.status is False
    assert result.error == PrintProductErrors.PRINT_PRODUCT_CATEGORY_NOT_FOUND.value

# ========== SYNC ==========

def test_sync_print_product_categories(client, clean_categories):
    with patch('server.config.sinalite.get_product_categories', return_value=[CATEGORY_BUSINESS_CARDS, CATEGORY_FLYERS]):
        result = PrintProductController.sync_print_product_categories()
        assert result.status is True
        assert result.data == {"message": PrintProductSuccessMessages.PRINT_PRODUCT_CATEGORY_IN_SYNC.value}
        assert PrintProductCategory.query.count() == 2

# ========== SINALITE PRODUCTS ==========

def test_get_all_products(client):
    with patch('server.config.sinalite.get_products', return_value=[{"id": 1, "name": "Business Card"}]):
        result = PrintProductController.get_all_products()
        assert result.status is True
        assert result.data[0]["name"] == "Business Card"

    with patch('server.config.sinalite.get_products', return_value=[]):
        result = PrintProductController.get_all_products()
        assert result.status is False
        assert result.error == PrintProductErrors.FAILED_TO_FETCH_PRINT_PRODUCTS.value

def test_get_products_by_category(client, create_categories):
    with patch('server.config.sinalite.get_products', return_value=[
        {"id": 1, "name": "Premium BC", "category": CATEGORY_BUSINESS_CARDS},
        {"id": 2, "name": "Standard BC", "category": CATEGORY_BUSINESS_CARDS}
    ]):
        result = PrintProductController.get_products_by_category(CATEGORY_BUSINESS_CARDS)
        assert result.status is True
        assert len(result.data) == 2

        result = PrintProductController.get_products_by_category(CATEGORY_FLYERS)
        assert result.status is False
        assert result.error == PrintProductErrors.PRINT_PRODUCT_CATEGORY_NOT_FOUND.value

        result = PrintProductController.get_products_by_category("Shirts")
        assert result.status is False
        assert result.error == PrintProductErrors.PRINT_PRODUCT_CATEGORY_NOT_FOUND.value

    with patch('server.config.sinalite.get_products', return_value=[]):
        result = PrintProductController.get_products_by_category(CATEGORY_POSTERS)
        assert result.status is True
        assert result.data == []

# ========== update_print_product_category ==========

def test_update_print_product_category_description(client, create_categories):
    category, _, _ = create_categories
    result = PrintProductController.update_print_product_category(category.id, description="New description")

    assert result.status is True
    assert result.data["message"] == PrintProductSuccessMessages.PRODUCT_CATEGORY_UPDATED_SUCCESSFULLY.value
    updated = db.session.get(PrintProductCategory, category.id)
    assert updated.description == "New description"

def test_update_print_product_category_invalid_description(client, create_categories):
    category, _, _ = create_categories
    long_desc = "a" * 1001
    result = PrintProductController.update_print_product_category(category.id, description=long_desc)
    assert result.status is False
    assert result.error == PrintProductErrors.PRINT_PRODUCT_DESCRIPTION_TOO_LONG.value

def test_update_print_product_category_image_url(client, create_categories):
    category, _, _ = create_categories
    result = PrintProductController.update_print_product_category(category.id, image="https://example.com/image.jpg")
    assert result.status is True
    updated = db.session.get(PrintProductCategory, category.id)
    assert updated.image == "https://example.com/image.jpg"

def test_update_print_product_category_invalid_image_url(client, create_categories):
    category, _, _ = create_categories
    result = PrintProductController.update_print_product_category(category.id, image="ftp://invalid-url.com")
    assert result.status is False
    assert result.error == PrintProductErrors.INVALID_IMAGE_URL.value

def test_update_print_product_category_not_found(client):
    result = PrintProductController.update_print_product_category(9999, description="No such category")
    assert result.status is False
    assert result.error == PrintProductErrors.PRINT_PRODUCT_CATEGORY_NOT_FOUND.value
