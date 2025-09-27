import pytest
import io
from unittest.mock import MagicMock, patch
from werkzeug.datastructures import FileStorage
from server.controllers.print_product_controller import (
    PrintProductController,
    PrintProductErrors,
    PrintProductSuccessMessages
)
from server.models.print_product import PrintProductCategory, PrintProductType
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

@pytest.fixture
def clean_product_types():
    PrintProductType.query.delete()
    db.session.commit()
    yield
    PrintProductType.query.delete()
    db.session.commit()

@pytest.fixture
def create_product_types(create_categories):
    category1, _, _ = create_categories
    
    # Create some product types for testing
    type1 = PrintProductType(
        name="Premium Business Cards",
        category_id=category1.id,
        description="High-quality business cards with premium finish"
    )
    type2 = PrintProductType(
        name="Standard Business Cards",
        category_id=category1.id,
        description="Standard business cards with basic finish"
    )
    
    db.session.add_all([type1, type2])
    db.session.commit()
    
    # Re-attach for access to IDs
    return (
        db.session.get(PrintProductType, type1.id),
        db.session.get(PrintProductType, type2.id),
        category1
    )

@pytest.fixture
def create_products(create_categories):
    """Create products in the database for testing"""
    from server.models.print_product import PrintProduct
    
    category1, _, _ = create_categories
    
    # Create products with IDs that match what Sinalite API returns
    product1 = PrintProduct(
        name="Premium Business Cards",
        sku="businesscard_14pt_premium",
        description="High-quality business cards",
        category_id=category1.id,
        type_id=0  # Unclassified
    )
    product2 = PrintProduct(
        name="Standard Business Cards", 
        sku="businesscard_14pt_standard",
        description="Standard business cards",
        category_id=category1.id,
        type_id=0  # Unclassified
    )
    product3 = PrintProduct(
        name="Flyer Product",
        sku="flyer_standard",
        description="Standard flyer",
        category_id=category1.id,  # Wrong category but exists in DB
        type_id=0
    )
    
    db.session.add_all([product1, product2, product3])
    db.session.commit()
    
    # Get the products with their assigned IDs
    db_product1 = db.session.get(PrintProduct, product1.id)
    db_product2 = db.session.get(PrintProduct, product2.id)
    db_product3 = db.session.get(PrintProduct, product3.id)
    
    return (
        db_product1,
        db_product2,
        db_product3,
        category1
    )

@pytest.fixture
def clean_products():
    """Clean up products table"""
    from server.models.print_product import PrintProduct
    PrintProduct.query.delete()
    db.session.commit()
    yield
    PrintProduct.query.delete()
    db.session.commit()

# ========== EMPTY TABLE COVERAGE ==========

def test_get_all_product_categories_empty_table(client, clean_categories):
    result = PrintProductController.get_all_product_categories()
    assert isinstance(result, Result)
    assert result.status is True
    assert result.data == []
    assert result.error is None

def test_get_enabled_product_categories_empty_table(client, clean_categories):
    result = PrintProductController.get_enabled_product_categories()
    assert isinstance(result, Result)
    assert result.status is True
    assert result.data == []
    assert result.error is None

def test_update_print_product_category_status_empty_table(client, clean_categories):
    result = PrintProductController.update_print_product_category_status(1, True)
    assert isinstance(result, Result)
    assert result.status is True  # Still true, just returns empty list
    assert result.data == []
    assert result.error is None

def test_get_all_products_by_category_empty_table(client, clean_categories):
    result = PrintProductController.get_all_products_by_category(1)
    assert isinstance(result, Result)
    assert result.status is True
    assert result.data == []
    assert result.error is None

def test_get_enabled_products_by_category_empty_table(client, clean_categories, clean_products):
    result = PrintProductController.get_enabled_products_by_category(1)
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

def test_get_all_products_by_category_success(client, create_products):
    """Test get_all_products_by_category with valid category ID"""
    product1, product2, _, category1 = create_products
    
    result = PrintProductController.get_all_products_by_category(category1.id)
    assert result.status is True
    assert len(result.data) == 3  # All 3 products are in this category
    assert all(product["category_id"] == category1.id for product in result.data)
    
    # Verify the returned products match our database products
    product_ids = [product["id"] for product in result.data]
    assert product1.id in product_ids
    assert product2.id in product_ids

def test_get_all_products_by_category_not_found(client, create_categories):
    """Test get_all_products_by_category with non-existent category ID"""
    with patch('server.config.sinalite.get_products', return_value=[{"id": 1, "name": "Business Card"}]):
        result = PrintProductController.get_all_products_by_category(9999)
        assert result.status is False
        assert result.error == PrintProductErrors.PRINT_PRODUCT_CATEGORY_NOT_FOUND.value

def test_get_enabled_products_by_category_success(client, create_products):
    """Test get_enabled_products_by_category with valid enabled category ID and products in DB"""
    product1, product2, _, category1 = create_products
    
    with patch('server.config.sinalite.get_products', return_value=[
        {"id": product1.id, "sku": "businesscard_14pt_premium", "name": "Premium BC", "category": CATEGORY_BUSINESS_CARDS, "enabled": 1},
        {"id": product2.id, "sku": "businesscard_14pt_standard", "name": "Standard BC", "category": CATEGORY_BUSINESS_CARDS, "enabled": 1},
        {"id": 999, "sku": "poster_standard", "name": "Poster", "category": CATEGORY_POSTERS, "enabled": 1}
    ]):
        result = PrintProductController.get_enabled_products_by_category(category1.id)
        assert result.status is True
        assert len(result.data) == 2
        assert all(product["category"] == CATEGORY_BUSINESS_CARDS for product in result.data)
        # Verify only products with matching IDs in DB are returned
        ids = [product["id"] for product in result.data]
        assert product1.id in ids
        assert product2.id in ids
        assert 999 not in ids  # Not in our DB

def test_get_enabled_products_by_category_disabled_category(client, create_categories):
    """Test get_enabled_products_by_category with disabled category ID"""
    _, category2, _ = create_categories  # category2 is disabled
    
    with patch('server.config.sinalite.get_products', return_value=[
        {"id": 1, "name": "Flyer", "category": CATEGORY_FLYERS}
    ]):
        result = PrintProductController.get_enabled_products_by_category(category2.id)
        assert result.status is False
        assert result.error == PrintProductErrors.PRINT_PRODUCT_CATEGORY_NOT_FOUND.value

def test_get_enabled_products_by_category_not_found(client, create_categories):
    """Test get_enabled_products_by_category with non-existent category ID"""
    with patch('server.config.sinalite.get_products', return_value=[{"id": 1, "name": "Business Card"}]):
        result = PrintProductController.get_enabled_products_by_category(9999)
        assert result.status is False
        assert result.error == PrintProductErrors.PRINT_PRODUCT_CATEGORY_NOT_FOUND.value

def test_get_all_products_by_category_no_matching_products(client, create_categories):
    """Test get_all_products_by_category when no products exist in the category"""
    _, category2, _ = create_categories  # category2 has no products
    
    result = PrintProductController.get_all_products_by_category(category2.id)
    assert result.status is True
    assert result.data == []

def test_get_enabled_products_by_category_no_matching_products(client, create_products):
    """Test get_enabled_products_by_category when no products match the category"""
    _, _, _, category1 = create_products
    
    with patch('server.config.sinalite.get_products', return_value=[
        {"id": 1, "sku": "flyer_standard", "name": "Flyer", "category": CATEGORY_FLYERS, "enabled": 1},
        {"id": 2, "sku": "poster_standard", "name": "Poster", "category": CATEGORY_POSTERS, "enabled": 1}
    ]):
        result = PrintProductController.get_enabled_products_by_category(category1.id)
        assert result.status is True
        assert result.data == []

def test_get_enabled_products_by_category_sinalite_disabled_products(client, create_products):
    """Test get_enabled_products_by_category filters out disabled products from Sinalite API"""
    product1, product2, _, category1 = create_products
    
    with patch('server.config.sinalite.get_products', return_value=[
        {"id": product1.id, "sku": "businesscard_14pt_premium", "name": "Premium BC", "category": CATEGORY_BUSINESS_CARDS, "enabled": 0},  # Disabled
        {"id": product2.id, "sku": "businesscard_14pt_standard", "name": "Standard BC", "category": CATEGORY_BUSINESS_CARDS, "enabled": 1},  # Enabled
        {"id": 888, "sku": "businesscard_14pt_extra", "name": "Extra BC", "category": CATEGORY_BUSINESS_CARDS, "enabled": 1}  # Enabled but not in DB
    ]):
        result = PrintProductController.get_enabled_products_by_category(category1.id)
        assert result.status is True
        assert len(result.data) == 1
        assert result.data[0]["id"] == product2.id  # Only the enabled one in DB

def test_get_enabled_products_by_category_missing_from_database(client, create_products):
    """Test get_enabled_products_by_category filters out products not in our database"""
    product1, product2, _, category1 = create_products
    
    with patch('server.config.sinalite.get_products', return_value=[
        {"id": product1.id, "sku": "businesscard_14pt_premium", "name": "Premium BC", "category": CATEGORY_BUSINESS_CARDS, "enabled": 1},  # In DB
        {"id": product2.id, "sku": "businesscard_14pt_standard", "name": "Standard BC", "category": CATEGORY_BUSINESS_CARDS, "enabled": 1},  # In DB
        {"id": 777, "sku": "businesscard_14pt_new", "name": "New BC", "category": CATEGORY_BUSINESS_CARDS, "enabled": 1},  # Not in DB
        {"id": 666, "sku": "businesscard_14pt_another", "name": "Another BC", "category": CATEGORY_BUSINESS_CARDS, "enabled": 1}  # Not in DB
    ]):
        result = PrintProductController.get_enabled_products_by_category(category1.id)
        assert result.status is True
        assert len(result.data) == 2
        # Only products that exist in our database should be returned
        ids = [product["id"] for product in result.data]
        assert product1.id in ids
        assert product2.id in ids
        assert 777 not in ids
        assert 666 not in ids

def test_get_enabled_products_by_category_mixed_conditions(client, create_products):
    """Test get_enabled_products_by_category with mixed conditions (enabled/disabled, in DB/not in DB)"""
    product1, product2, product3, category1 = create_products
    
    with patch('server.config.sinalite.get_products', return_value=[
        # Should be included: enabled + in DB + correct category
        {"id": product1.id, "sku": "businesscard_14pt_premium", "name": "Premium BC", "category": CATEGORY_BUSINESS_CARDS, "enabled": 1},
        # Should be excluded: disabled + in DB + correct category
        {"id": product2.id, "sku": "businesscard_14pt_standard", "name": "Standard BC", "category": CATEGORY_BUSINESS_CARDS, "enabled": 0},
        # Should be excluded: enabled + not in DB + correct category
        {"id": 555, "sku": "businesscard_14pt_new", "name": "New BC", "category": CATEGORY_BUSINESS_CARDS, "enabled": 1},
        # Should be excluded: enabled + in DB + wrong category
        {"id": product3.id, "sku": "flyer_standard", "name": "Flyer", "category": CATEGORY_FLYERS, "enabled": 1},
        # Should be excluded: disabled + not in DB + wrong category
        {"id": 444, "sku": "poster_standard", "name": "Poster", "category": CATEGORY_POSTERS, "enabled": 0}
    ]):
        result = PrintProductController.get_enabled_products_by_category(category1.id)
        assert result.status is True
        assert len(result.data) == 1
        assert result.data[0]["id"] == product1.id

def test_get_enabled_products_by_category_batch_query_performance(client, create_products):
    """Test get_enabled_products_by_category with many products to verify batch query optimization"""
    product1, product2, _, category1 = create_products
    
    # Create a large number of products from Sinalite API
    sinalite_products = []
    for i in range(100):  # 100 products
        sinalite_products.append({
            "id": i + 1000,  # Use high IDs to avoid conflicts
            "sku": f"businesscard_14pt_product_{i}",
            "name": f"Product {i}",
            "category": CATEGORY_BUSINESS_CARDS,
            "enabled": 1 if i % 2 == 0 else 0  # Alternate enabled/disabled
        })
    
    # Add our existing products to the mix
    sinalite_products.extend([
        {"id": product1.id, "sku": "businesscard_14pt_premium", "name": "Premium BC", "category": CATEGORY_BUSINESS_CARDS, "enabled": 1},
        {"id": product2.id, "sku": "businesscard_14pt_standard", "name": "Standard BC", "category": CATEGORY_BUSINESS_CARDS, "enabled": 1},
        {"id": 2000, "sku": "businesscard_14pt_extra", "name": "Extra BC", "category": CATEGORY_BUSINESS_CARDS, "enabled": 1}
    ])
    
    with patch('server.config.sinalite.get_products', return_value=sinalite_products):
        result = PrintProductController.get_enabled_products_by_category(category1.id)
        assert result.status is True
        # Should return only the 2 products that exist in our database and are enabled
        assert len(result.data) == 2
        ids = [product["id"] for product in result.data]
        assert product1.id in ids
        assert product2.id in ids

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

# ========== update_print_product_category ==========

def test_update_print_product_category_description(client, create_categories):
    category, _, _ = create_categories
    result = PrintProductController.update_print_product_category(category.id, description="New description")

    assert result.status is True
    assert result.data["message"] == PrintProductSuccessMessages.PRODUCT_CATEGORY_UPDATED_SUCCESSFULLY.value
    updated = db.session.get(PrintProductCategory, category.id)
    assert updated.description == "New description"

def test_update_print_product_category_description_too_long(client, create_categories):
    category, _, _ = create_categories
    long_desc = "a" * 1001
    result = PrintProductController.update_print_product_category(category.id, description=long_desc)

    assert result.status is False
    assert result.error == PrintProductErrors.PRINT_PRODUCT_DESCRIPTION_TOO_LONG.value

def test_update_print_product_category_not_found(client):
    result = PrintProductController.update_print_product_category(category_id=9999, description="Doesn't matter")

    assert result.status is False
    assert result.error == PrintProductErrors.PRINT_PRODUCT_CATEGORY_NOT_FOUND.value

def test_update_print_product_category_invalid_image_type(client, create_categories):
    category, _, _ = create_categories
    result = PrintProductController.update_print_product_category(category.id, image=12345)

    assert result.status is False
    assert result.error == PrintProductErrors.INVALID_IMAGE_FILE.value

def test_update_print_product_category_empty_image_file(client, create_categories):
    category, _, _ = create_categories
    # Create FileStorage with empty filename but some content to ensure it's a valid FileStorage object
    empty_image = FileStorage(stream=io.BytesIO(b"some content"), filename="", content_type="image/png")
    result = PrintProductController.update_print_product_category(category.id, image=empty_image)

    assert result.status is False
    assert result.error == PrintProductErrors.EMPTY_IMAGE_FILENAME.value

def test_update_print_product_category_valid_image(client, create_categories):
    category, _, _ = create_categories
    image_data = FileStorage(stream=io.BytesIO(b"fake image data"), filename="test.png", content_type="image/png")
    
    with patch("server.controllers.print_product_controller.current_app") as mock_current_app:
        fake_storage = MagicMock()
        fake_storage.upload_file.return_value = "http://example.com/image.png"
        mock_current_app.extensions = {"filestorage": fake_storage}
        
        result = PrintProductController.update_print_product_category(category.id, image=image_data)
        
        assert result.status is True
        assert result.data["message"] == PrintProductSuccessMessages.PRODUCT_CATEGORY_UPDATED_SUCCESSFULLY.value
        updated = db.session.get(PrintProductCategory, category.id)
        assert updated.image == "http://example.com/image.png"

def test_update_print_product_category_commit_fails(client, create_categories):
    category, _, _ = create_categories
    
    with patch("server.controllers.print_product_controller.db.session.commit", side_effect=Exception("Database fail")):
        result = PrintProductController.update_print_product_category(category.id, description="Should fail")
        
        assert result.status is False
        assert PrintProductErrors.FAILED_TO_UPDATE_PRODUCT_CATEGORY.value in result.error

# ========== PRINT PRODUCT TYPE TESTS ==========

# ========== GET ALL PRINT PRODUCT TYPES TESTS ==========

def test_get_all_print_product_types_empty_table(client, clean_product_types):
    """Test get_all_print_product_types when table is empty"""
    result = PrintProductController.get_all_print_product_types()
    
    assert isinstance(result, Result)
    assert result.status is True
    assert result.data == []
    assert result.error is None

def test_get_all_print_product_types_success(client, create_product_types):
    """Test successful retrieval of all print product types"""
    product_type1, product_type2, _ = create_product_types
    
    result = PrintProductController.get_all_print_product_types()
    
    assert isinstance(result, Result)
    assert result.status is True
    assert len(result.data) == 2
    assert result.error is None
    
    # Verify data structure and sorting (should be sorted by name)
    assert result.data[0]['name'] == "Premium Business Cards"  # Alphabetically first
    assert result.data[1]['name'] == "Standard Business Cards"  # Alphabetically second
    
    # Verify all required fields are present
    for product_type in result.data:
        assert 'id' in product_type
        assert 'name' in product_type
        assert 'category_id' in product_type
        assert 'description' in product_type
        assert 'image' in product_type
        assert 'created_at' in product_type
        assert 'updated_at' in product_type

def test_get_all_print_product_types_with_mixed_data(client, create_categories):
    """Test retrieval with mixed product types including some with images"""
    category1, category2, _ = create_categories
    
    # Create product types with different attributes
    type1 = PrintProductType(
        name="Type A",
        category_id=category1.id,
        description="Description A",
        image="http://example.com/image1.jpg"
    )
    type2 = PrintProductType(
        name="Type B", 
        category_id=category2.id,
        description="Description B",
        image=None
    )
    type3 = PrintProductType(
        name="Type C",
        category_id=category1.id,
        description="Description C",
        image="http://example.com/image3.jpg"
    )
    
    db.session.add_all([type1, type2, type3])
    db.session.commit()
    
    result = PrintProductController.get_all_print_product_types()
    
    assert result.status is True
    assert len(result.data) == 3
    
    # Should be sorted alphabetically by name
    names = [pt['name'] for pt in result.data]
    assert names == ["Type A", "Type B", "Type C"]
    
    # Verify image handling
    type_a = next(pt for pt in result.data if pt['name'] == "Type A")
    type_b = next(pt for pt in result.data if pt['name'] == "Type B")
    
    assert type_a['image'] == "http://example.com/image1.jpg"
    assert type_b['image'] is None

def test_get_all_print_product_types_database_error(client):
    """Test get_all_print_product_types when database query fails"""
    with patch("server.controllers.print_product_controller.PrintProductType.query") as mock_query:
        # Mock first() to fail immediately (this will trigger the exception handling)
        mock_query.first.side_effect = Exception("Database connection failed")
        
        result = PrintProductController.get_all_print_product_types()
        
        assert result.status is False
        assert PrintProductErrors.FAILED_TO_FETCH_PRINT_PRODUCT_TYPES.value in result.error
        assert "Database connection failed" in result.error

def test_get_all_print_product_types_query_failure(client):
    """Test get_all_print_product_types when query.all() fails"""
    with patch("server.controllers.print_product_controller.PrintProductType.query") as mock_query:
        # Mock first() to return a dummy object (not None) so the method continues
        mock_first = MagicMock()
        mock_first.id = 1  # Dummy object to represent "table not empty"
        mock_query.first.return_value = mock_first
        
        # Mock the order_by().all() chain to fail
        mock_order_by = MagicMock()
        mock_order_by.all.side_effect = Exception("Query execution failed")
        mock_query.order_by.return_value = mock_order_by
        
        result = PrintProductController.get_all_print_product_types()
        assert result.status is False
        assert PrintProductErrors.FAILED_TO_FETCH_PRINT_PRODUCT_TYPES.value in result.error
        assert "Query execution failed" in result.error


# ========== CREATE PRINT PRODUCT TYPE TESTS ==========

def test_create_print_product_type_success(client, create_categories):
    """Test successful creation of a print product type"""
    category, _, _ = create_categories
    
    data = {
        'name': 'New Business Card Type',
        'category_id': category.id,
        'description': 'A new type of business card'
    }
    
    result = PrintProductController.create_print_product_type(data)
    
    assert result.status is True
    assert result.data['name'] == 'New Business Card Type'
    assert result.data['category_id'] == category.id
    assert result.data['description'] == 'A new type of business card'
    assert result.data['image'] is None

def test_create_print_product_type_with_image(client, create_categories):
    """Test successful creation of a print product type with image"""
    category, _, _ = create_categories
    
    data = {
        'name': 'Business Card with Image',
        'category_id': category.id,
        'description': 'Business card type with image',
        'image': 'http://example.com/image.jpg'
    }
    
    result = PrintProductController.create_print_product_type(data)
    
    assert result.status is True
    assert result.data['name'] == 'Business Card with Image'
    assert result.data['image'] == 'http://example.com/image.jpg'

def test_create_print_product_type_name_required(client, create_categories):
    """Test creation fails when name is missing"""
    category, _, _ = create_categories
    
    data = {
        'category_id': category.id,
        'description': 'Description without name'
    }
    
    result = PrintProductController.create_print_product_type(data)
    
    assert result.status is False
    assert result.error == PrintProductErrors.PRODUCT_TYPE_NAME_REQUIRED.value

def test_create_print_product_type_category_id_required(client, create_categories):
    """Test creation fails when category_id is missing"""
    category, _, _ = create_categories
    
    data = {
        'name': 'Business Card Type',
        'description': 'Description without category'
    }
    
    result = PrintProductController.create_print_product_type(data)
    
    assert result.status is False
    assert result.error == PrintProductErrors.PRODUCT_TYPE_CATEGORY_ID_REQUIRED.value

def test_create_print_product_type_description_required(client, create_categories):
    """Test creation fails when description is missing"""
    category, _, _ = create_categories
    
    data = {
        'name': 'Business Card Type',
        'category_id': category.id
    }
    
    result = PrintProductController.create_print_product_type(data)
    
    assert result.status is False
    assert result.error == PrintProductErrors.PRODUCT_TYPE_DESCRIPTION_REQUIRED.value

def test_create_print_product_type_name_too_short(client, create_categories):
    """Test creation fails when name is too short"""
    category, _, _ = create_categories
    
    data = {
        'name': 'A',  # Only 1 character
        'category_id': category.id,
        'description': 'Description'
    }
    
    result = PrintProductController.create_print_product_type(data)
    
    assert result.status is False
    assert result.error == PrintProductErrors.PRODUCT_TYPE_NAME_TOO_SHORT.value

def test_create_print_product_type_name_too_long(client, create_categories):
    """Test creation fails when name is too long"""
    category, _, _ = create_categories
    
    data = {
        'name': 'A' * 256,  # 256 characters (exceeds 255 limit)
        'category_id': category.id,
        'description': 'Description'
    }
    
    result = PrintProductController.create_print_product_type(data)
    
    assert result.status is False
    assert result.error == PrintProductErrors.PRODUCT_TYPE_NAME_TOO_LONG.value

def test_create_print_product_type_category_not_found(client, create_categories):
    """Test creation fails when category doesn't exist"""
    data = {
        'name': 'Business Card Type',
        'category_id': 9999,  # Non-existent category
        'description': 'Description'
    }
    
    result = PrintProductController.create_print_product_type(data)
    
    assert result.status is False
    assert result.error == PrintProductErrors.PRODUCT_TYPE_CATEGORY_NOT_FOUND.value

def test_create_print_product_type_name_already_exists(client, create_categories):
    """Test creation fails when name already exists in the same category"""
    category, _, _ = create_categories
    
    # First creation should succeed
    data1 = {
        'name': 'Duplicate Name',
        'category_id': category.id,
        'description': 'First description'
    }
    result1 = PrintProductController.create_print_product_type(data1)
    assert result1.status is True
    
    # Second creation with same name in same category should fail
    data2 = {
        'name': 'Duplicate Name',
        'category_id': category.id,
        'description': 'Second description'
    }
    result2 = PrintProductController.create_print_product_type(data2)
    
    assert result2.status is False
    assert result2.error == PrintProductErrors.PRODUCT_TYPE_NAME_ALREADY_EXISTS.value

def test_create_print_product_type_same_name_different_category(client, create_categories):
    """Test creation succeeds when same name exists in different category"""
    category1, category2, _ = create_categories
    
    # First creation in category1
    data1 = {
        'name': 'Same Name',
        'category_id': category1.id,
        'description': 'First description'
    }
    result1 = PrintProductController.create_print_product_type(data1)
    assert result1.status is True
    
    # Second creation with same name in category2 should succeed
    data2 = {
        'name': 'Same Name',
        'category_id': category2.id,
        'description': 'Second description'
    }
    result2 = PrintProductController.create_print_product_type(data2)
    
    assert result2.status is True
    assert result2.data['name'] == 'Same Name'
    assert result2.data['category_id'] == category2.id

def test_create_print_product_type_commit_fails(client, create_categories):
    """Test creation fails when database commit fails"""
    category, _, _ = create_categories
    
    data = {
        'name': 'Business Card Type',
        'category_id': category.id,
        'description': 'Description'
    }
    
    with patch("server.controllers.print_product_controller.db.session.commit", side_effect=Exception("Database fail")):
        result = PrintProductController.create_print_product_type(data)
        
        assert result.status is False
        assert PrintProductErrors.FAILED_TO_CREATE_PRODUCT_TYPE.value in result.error

# ========== UPDATE PRINT PRODUCT TYPE TESTS ==========

def test_update_print_product_type_description_success(client, create_product_types):
    """Test successful update of product type description"""
    product_type, _, _ = create_product_types
    
    result = PrintProductController.update_print_product_type(
        product_type.id, 
        description="Updated description"
    )
    
    assert result.status is True
    assert result.data["message"] == PrintProductSuccessMessages.PRODUCT_TYPE_UPDATED_SUCCESSFULLY.value
    
    # Verify database was updated
    updated = db.session.get(PrintProductType, product_type.id)
    assert updated.description == "Updated description"

def test_update_print_product_type_image_success(client, create_product_types):
    """Test successful update of product type image"""
    product_type, _, _ = create_product_types
    
    image_data = FileStorage(
        stream=io.BytesIO(b"fake image data"), 
        filename="test.png", 
        content_type="image/png"
    )
    
    with patch("server.controllers.print_product_controller.current_app") as mock_current_app:
        fake_storage = MagicMock()
        fake_storage.upload_file.return_value = "http://example.com/new_image.png"
        mock_current_app.extensions = {"filestorage": fake_storage}
        
        result = PrintProductController.update_print_product_type(
            product_type.id, 
            image=image_data
        )
        
        assert result.status is True
        assert result.data["message"] == PrintProductSuccessMessages.PRODUCT_TYPE_UPDATED_SUCCESSFULLY.value
        
        # Verify database was updated
        updated = db.session.get(PrintProductType, product_type.id)
        assert updated.image == "http://example.com/new_image.png"

def test_update_print_product_type_both_description_and_image(client, create_product_types):
    """Test successful update of both description and image"""
    product_type, _, _ = create_product_types
    
    image_data = FileStorage(
        stream=io.BytesIO(b"fake image data"), 
        filename="test.png", 
        content_type="image/png"
    )
    
    with patch("server.controllers.print_product_controller.current_app") as mock_current_app:
        fake_storage = MagicMock()
        fake_storage.upload_file.return_value = "http://example.com/combined.png"
        mock_current_app.extensions = {"filestorage": fake_storage}
        
        result = PrintProductController.update_print_product_type(
            product_type.id, 
            description="Combined update",
            image=image_data
        )
        
        assert result.status is True
        assert result.data["message"] == PrintProductSuccessMessages.PRODUCT_TYPE_UPDATED_SUCCESSFULLY.value
        
        # Verify both were updated
        updated = db.session.get(PrintProductType, product_type.id)
        assert updated.description == "Combined update"
        assert updated.image == "http://example.com/combined.png"

def test_update_print_product_type_not_found(client):
    """Test update fails when product type doesn't exist"""
    result = PrintProductController.update_print_product_type(
        9999, 
        description="Doesn't matter"
    )
    
    assert result.status is False
    assert result.error == PrintProductErrors.PRINT_PRODUCT_TYPE_NOT_FOUND.value

def test_update_print_product_type_description_too_long(client, create_product_types):
    """Test update fails when description is too long"""
    product_type, _, _ = create_product_types
    
    long_desc = "a" * 1001  # Exceeds 1000 character limit
    
    result = PrintProductController.update_print_product_type(
        product_type.id, 
        description=long_desc
    )
    
    assert result.status is False
    assert result.error == PrintProductErrors.PRINT_PRODUCT_DESCRIPTION_TOO_LONG.value

def test_update_print_product_type_invalid_image_type(client, create_product_types):
    """Test update fails when image is not FileStorage"""
    product_type, _, _ = create_product_types
    
    result = PrintProductController.update_print_product_type(
        product_type.id, 
        image="not a file"
    )
    
    assert result.status is False
    assert result.error == PrintProductErrors.INVALID_IMAGE_FILE.value

def test_update_print_product_type_empty_image_filename(client, create_product_types):
    """Test update fails when image filename is empty"""
    product_type, _, _ = create_product_types
    
    empty_image = FileStorage(
        stream=io.BytesIO(b"some content"), 
        filename="", 
        content_type="image/png"
    )
    
    result = PrintProductController.update_print_product_type(
        product_type.id, 
        image=empty_image
    )
    
    assert result.status is False
    assert result.error == PrintProductErrors.EMPTY_IMAGE_FILENAME.value

def test_update_print_product_type_commit_fails(client, create_product_types):
    """Test update fails when database commit fails"""
    product_type, _, _ = create_product_types
    
    with patch("server.controllers.print_product_controller.db.session.commit", side_effect=Exception("Database fail")):
        result = PrintProductController.update_print_product_type(
            product_type.id, 
            description="Should fail"
        )
        
        assert result.status is False
        assert PrintProductErrors.FAILED_TO_UPDATE_PRODUCT_TYPE.value in result.error

# ========== DELETE PRINT PRODUCT TYPE TESTS ==========

def test_delete_print_product_type_success(client, create_product_types):
    """Test successful deletion of a print product type"""
    product_type, _, _ = create_product_types
    
    result = PrintProductController.delete_print_product_type(product_type.id)
    
    assert result.status is True
    assert result.data["message"] == PrintProductSuccessMessages.PRODUCT_TYPE_DELETED_SUCCESSFULLY.value
    
    # Verify it was deleted from database
    deleted = db.session.get(PrintProductType, product_type.id)
    assert deleted is None

def test_delete_print_product_type_not_found(client):
    """Test deletion fails when product type doesn't exist"""
    result = PrintProductController.delete_print_product_type(9999)
    
    assert result.status is False
    assert result.error == PrintProductErrors.PRINT_PRODUCT_TYPE_NOT_FOUND.value

def test_delete_print_product_type_in_use(client, create_product_types):
    """Test deletion fails when product type is being used by products"""
    product_type, _, _ = create_product_types
    
    # Create a mock product object that will be returned by the query
    mock_product = MagicMock()
    mock_product.id = 1
    mock_product.name = "Product using type"
    
    with patch('server.models.print_product.PrintProduct.query') as mock_query:
        # Mock the filter_by().first() chain
        mock_filter_by = MagicMock()
        mock_filter_by.first.return_value = mock_product
        mock_query.filter_by.return_value = mock_filter_by
        
        result = PrintProductController.delete_print_product_type(product_type.id)
        assert result.status is False
        assert result.error == PrintProductErrors.PRODUCT_TYPE_IN_USE.value
        
        # Verify it was not deleted from database
        not_deleted = db.session.get(PrintProductType, product_type.id)
        assert not_deleted is not None

def test_delete_print_product_type_commit_fails(client, create_product_types):
    """Test deletion fails when database commit fails"""
    product_type, _, _ = create_product_types
    
    with patch("server.controllers.print_product_controller.db.session.commit", side_effect=Exception("Database fail")):
        result = PrintProductController.delete_print_product_type(product_type.id)
        
        assert result.status is False
        assert PrintProductErrors.FAILED_TO_DELETE_PRODUCT_TYPE.value in result.error

# ========== SYNC PRINT PRODUCTS ==========

def test_sync_print_products_success_new_products(client, create_categories):
    """Test successful sync of new products from Sinalite API"""
    category1, _, _ = create_categories
    
    with patch('server.config.sinalite.get_products', return_value=[
        {"id": 1, "sku": "businesscard_14pt_premium", "name": "Premium BC", "category": CATEGORY_BUSINESS_CARDS, "enabled": 1},
        {"id": 2, "sku": "businesscard_14pt_standard", "name": "Standard BC", "category": CATEGORY_BUSINESS_CARDS, "enabled": 1},
        {"id": 3, "sku": "poster_standard", "name": "Poster", "category": CATEGORY_POSTERS, "enabled": 1}
    ]):
        result = PrintProductController.sync_print_products(category1.id)
        
        assert result.status is True
        assert result.data["message"] == PrintProductSuccessMessages.PRINT_PRODUCTS_SYNCED_SUCCESSFULLY.value
        assert result.data["products_added"] == 2  # Only business cards
        assert result.data["products_updated"] == 0
        assert result.data["total_products"] == 2
        
        # Verify products were created in database
        from server.models.print_product import PrintProduct
        db_products = PrintProduct.query.filter_by(category_id=category1.id).all()
        assert len(db_products) == 2
        assert any(p.sku == "businesscard_14pt_premium" for p in db_products)
        assert any(p.sku == "businesscard_14pt_standard" for p in db_products)

def test_sync_print_products_success_update_existing(client, create_products):
    """Test successful sync with existing products being updated"""
    product1, product2, _, category1 = create_products
    
    # Set initial descriptions
    product1.description = "Original description 1"
    product2.description = "Original description 2"
    db.session.commit()
    
    with patch('server.config.sinalite.get_products', return_value=[
        {"id": 1, "sku": product1.sku, "name": "Updated Premium BC", "category": CATEGORY_BUSINESS_CARDS, "enabled": 1},
        {"id": 2, "sku": product2.sku, "name": "Updated Standard BC", "category": CATEGORY_BUSINESS_CARDS, "enabled": 1},
        {"id": 3, "sku": "new_product", "name": "New Product", "category": CATEGORY_BUSINESS_CARDS, "enabled": 1}
    ]):
        result = PrintProductController.sync_print_products(category1.id)
        
        assert result.status is True
        assert result.data["products_added"] == 1  # New product
        assert result.data["products_updated"] == 2  # Existing products updated
        assert result.data["total_products"] == 3
        
        # Verify existing products were updated - only names, descriptions preserved
        from server.models.print_product import PrintProduct
        updated_product1 = db.session.get(PrintProduct, product1.id)
        updated_product2 = db.session.get(PrintProduct, product2.id)
        assert updated_product1.name == "Updated Premium BC"
        assert updated_product2.name == "Updated Standard BC"
        assert updated_product1.description == "Original description 1"  # Description preserved
        assert updated_product2.description == "Original description 2"  # Description preserved

def test_sync_print_products_category_not_found(client):
    """Test sync fails when category doesn't exist"""
    result = PrintProductController.sync_print_products(9999)
    
    assert result.status is False
    assert result.error == PrintProductErrors.PRINT_PRODUCT_CATEGORY_NOT_FOUND.value

def test_sync_print_products_sinalite_api_failure(client, create_categories):
    """Test sync fails when Sinalite API returns no products"""
    category1, _, _ = create_categories
    
    with patch('server.config.sinalite.get_products', return_value=[]):
        result = PrintProductController.sync_print_products(category1.id)
        
        assert result.status is False
        assert result.error == PrintProductErrors.FAILED_TO_FETCH_PRINT_PRODUCTS.value

def test_sync_print_products_no_matching_category(client, create_categories):
    """Test sync succeeds but returns no products when category doesn't match"""
    category1, _, _ = create_categories
    
    with patch('server.config.sinalite.get_products', return_value=[
        {"id": 1, "sku": "poster_standard", "name": "Poster", "category": CATEGORY_POSTERS, "enabled": 1},
        {"id": 2, "sku": "flyer_standard", "name": "Flyer", "category": CATEGORY_FLYERS, "enabled": 1}
    ]):
        result = PrintProductController.sync_print_products(category1.id)
        
        assert result.status is True
        assert result.data["message"] == "No products found in Sinalite for this category"
        assert result.data["products_added"] == 0
        assert result.data["products_updated"] == 0
        assert result.data["total_products"] == 0

def test_sync_print_products_skip_invalid_sku(client, create_categories):
    """Test sync skips products without SKU"""
    category1, _, _ = create_categories
    
    with patch('server.config.sinalite.get_products', return_value=[
        {"id": 1, "sku": "businesscard_14pt_premium", "name": "Premium BC", "category": CATEGORY_BUSINESS_CARDS, "enabled": 1},
        {"id": 2, "sku": "", "name": "Invalid Product", "category": CATEGORY_BUSINESS_CARDS, "enabled": 1},  # Empty SKU
        {"id": 3, "name": "No SKU Product", "category": CATEGORY_BUSINESS_CARDS, "enabled": 1}  # Missing SKU
    ]):
        result = PrintProductController.sync_print_products(category1.id)
        
        assert result.status is True
        assert result.data["products_added"] == 1  # Only the valid product
        assert result.data["products_updated"] == 0
        #assert result.data["total_products"] == 1

def test_sync_print_products_database_error_handling(client, create_categories):
    """Test sync handles database errors gracefully"""
    category1, _, _ = create_categories
    
    with patch('server.config.sinalite.get_products', return_value=[
        {"id": 1, "sku": "businesscard_14pt_premium", "name": "Premium BC", "category": CATEGORY_BUSINESS_CARDS, "enabled": 1}
    ]), patch('server.controllers.print_product_controller.db.session.commit', side_effect=Exception("Database error")):
        result = PrintProductController.sync_print_products(category1.id)
        
        assert result.status is False
        assert "Failed to sync print products: Database error" in result.error

def test_sync_print_products_updates_classification_status(client, create_categories):
    """Test sync updates category classification status after completion"""
    category1, _, _ = create_categories
    
    with patch('server.config.sinalite.get_products', return_value=[
        {"id": 1, "sku": "businesscard_14pt_premium", "name": "Premium BC", "category": CATEGORY_BUSINESS_CARDS, "enabled": 1}
    ]), patch('server.controllers.print_product_controller.PrintProductController.update_category_classification_status') as mock_update:
        result = PrintProductController.sync_print_products(category1.id)
        
        assert result.status is True
        mock_update.assert_called_once_with(category1.id)

def test_sync_print_products_mixed_add_and_update(client, create_products):
    """Test sync handles mixed scenario of adding new and updating existing products"""
    product1, _, _, category1 = create_products
    
    with patch('server.config.sinalite.get_products', return_value=[
        {"id": 1, "sku": product1.sku, "name": "Updated Name", "category": CATEGORY_BUSINESS_CARDS, "enabled": 1},  # Update existing
        {"id": 2, "sku": "new_product", "name": "New Product", "category": CATEGORY_BUSINESS_CARDS, "enabled": 1},  # Add new
        {"id": 3, "sku": "another_new", "name": "Another New", "category": CATEGORY_BUSINESS_CARDS, "enabled": 1}  # Add new
    ]):
        result = PrintProductController.sync_print_products(category1.id)
        
        assert result.status is True
        assert result.data["products_added"] == 2
        assert result.data["products_updated"] == 1
        assert result.data["total_products"] == 3

def test_sync_print_products_new_products_have_null_description(client, create_categories):
    """Test that new products created during sync have description set to None and vendor info set correctly"""
    category1, _, _ = create_categories
    
    with patch('server.config.sinalite.get_products', return_value=[
        {"id": 1, "sku": "new_product_1", "name": "New Product 1", "category": CATEGORY_BUSINESS_CARDS, "enabled": 1},
        {"id": 2, "sku": "new_product_2", "name": "New Product 2", "category": CATEGORY_BUSINESS_CARDS, "enabled": 1}
    ]):
        result = PrintProductController.sync_print_products(category1.id)
        
        assert result.status is True
        assert result.data["products_added"] == 2
        assert result.data["products_updated"] == 0
        assert result.data["total_products"] == 2
        
        # Verify new products were created with correct vendor information
        from server.models.print_product import PrintProduct
        new_product1 = PrintProduct.query.filter_by(sku="new_product_1").first()
        new_product2 = PrintProduct.query.filter_by(sku="new_product_2").first()
        
        assert new_product1 is not None
        assert new_product2 is not None
        assert new_product1.description is None  # Description should be None for new products
        assert new_product2.description is None  # Description should be None for new products
        assert new_product1.name == "New Product 1"
        assert new_product2.name == "New Product 2"
        
        # Verify vendor information is set correctly
        assert new_product1.vendor_id == 1  # Sinalite vendor ID
        assert new_product2.vendor_id == 1  # Sinalite vendor ID
        assert new_product1.vendor_product_id == "1"  # Sinalite's product ID
        assert new_product2.vendor_product_id == "2"  # Sinalite's product ID

def test_sync_print_products_updates_vendor_product_id(client, create_products):
    """Test that sync updates vendor_product_id for existing products when it changes"""
    product1, product2, _, category1 = create_products
    
    # Set initial vendor_product_id values
    product1.vendor_product_id = "old_id_1"
    product2.vendor_product_id = "old_id_2"
    db.session.commit()
    
    with patch('server.config.sinalite.get_products', return_value=[
        {"id": 999, "sku": product1.sku, "name": "Updated Product 1", "category": CATEGORY_BUSINESS_CARDS, "enabled": 1},  # Different vendor ID
        {"id": 888, "sku": product2.sku, "name": "Updated Product 2", "category": CATEGORY_BUSINESS_CARDS, "enabled": 1}   # Different vendor ID
    ]):
        result = PrintProductController.sync_print_products(category1.id)
        
        assert result.status is True
        assert result.data["products_added"] == 0
        assert result.data["products_updated"] == 2
        assert result.data["total_products"] == 2
        
        # Verify vendor_product_id was updated
        from server.models.print_product import PrintProduct
        updated_product1 = db.session.get(PrintProduct, product1.id)
        updated_product2 = db.session.get(PrintProduct, product2.id)
        
        assert updated_product1.vendor_product_id == "999"  # Updated from Sinalite
        assert updated_product2.vendor_product_id == "888"  # Updated from Sinalite
        assert updated_product1.name == "Updated Product 1"
        assert updated_product2.name == "Updated Product 2"

def test_get_all_vendors_success(client):
    """Test successful retrieval of all vendors"""
    from server.models.print_product import Vendor
    
    # Create test vendors
    vendor1 = Vendor(id=0, name="Native")
    vendor2 = Vendor(id=1, name="Sinalite")
    vendor3 = Vendor(id=2, name="Test Vendor")
    
    db.session.add_all([vendor1, vendor2, vendor3])
    db.session.commit()
    
    result = PrintProductController.get_all_vendors()
    
    assert result.status is True
    assert len(result.data) == 3
    
    # Should be sorted alphabetically by name
    names = [vendor['name'] for vendor in result.data]
    assert names == ["Native", "Sinalite", "Test Vendor"]
    
    # Verify vendor data structure
    for vendor in result.data:
        assert 'id' in vendor
        assert 'name' in vendor
        assert 'created_at' in vendor
        assert 'updated_at' in vendor

def test_get_all_vendors_empty_table(client):
    """Test get_all_vendors when table is empty"""
    from server.models.print_product import Vendor
    
    # Clean up vendors table
    Vendor.query.delete()
    db.session.commit()
    
    result = PrintProductController.get_all_vendors()
    
    assert result.status is True
    assert result.data == []

def test_get_all_vendors_database_error(client):
    """Test get_all_vendors when database query fails"""
    with patch("server.models.print_product.Vendor.query") as mock_query:
        mock_query.first.side_effect = Exception("Database connection failed")
        
        result = PrintProductController.get_all_vendors()
        
        assert result.status is False
        assert "Failed to fetch vendors" in result.error
        assert "Database connection failed" in result.error
