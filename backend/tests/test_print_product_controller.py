import pytest
from server.controllers.print_product_controller import PrintProductController, PrintProductErrors, PrintProductSuccessMessages
from server.models.print_product import PrintProductCategory
from server import database as db
from server.config import sinalite
from unittest.mock import patch
from server.controllers import Result

@pytest.fixture
def create_categories():
    category1 = PrintProductCategory(name="Business Cards", enabled=True)
    category2 = PrintProductCategory(name="Flyers", enabled=False)
    db.session.add_all([category1, category2])
    db.session.commit()
    return category1, category2

def test_get_all_product_categories(client, create_categories):
    result = PrintProductController.get_all_product_categories()
    assert isinstance(result, Result)
    assert result.status is True
    assert len(result.data) == 2
    assert result.error is None

def test_get_enabled_product_categories(client, create_categories):
    result = PrintProductController.get_enabled_product_categories()
    assert isinstance(result, Result)
    assert result.status is True
    assert len(result.data) == 1
    assert result.data[0]['name'] == "Business Cards"
    assert result.error is None

def test_update_print_product_category_status(client, create_categories):
    _, category2 = create_categories

    initial_category = db.session.get(PrintProductCategory, category2.id)
    assert initial_category.enabled is False

    # Valid catrgory id
    result = PrintProductController.update_print_product_category_status(category2.id, True)

    assert isinstance(result, Result)
    assert result.status is True
    assert result.data == PrintProductSuccessMessages.UPDATED_PRINT_PRODUCT_CATEGORY_STATUS_SUCCESSFULLY.value
    assert result.error is None

    updated_category = db.session.get(PrintProductCategory, category2.id)
    assert updated_category.enabled is True

    # Invalid category id
    result = PrintProductController.update_print_product_category_status(999, True)
    assert isinstance(result, Result)
    assert result.status == False
    assert result.data == None
    assert result.error == PrintProductErrors.PRINT_PRODUCT_CATEGORY_NOT_FOUND.value
    