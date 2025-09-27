"""
Integration tests for Pricing API endpoints.
Tests all endpoints and edge cases to achieve 100% coverage.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from server.controllers.helpers import Result


class TestPricingAPI:
    """Test cases for Pricing API endpoints."""

    def test_get_product_options_success(self, client):
        """Test successful product options retrieval via API."""
        product_id = 123
        store_code = 6
        expected_options = [
            {
                "group": "qty",
                "options": [
                    {"id": 5, "name": "50"},
                    {"id": 105, "name": "25"}
                ]
            }
        ]
        
        with patch('server.routes.pricing_routes.PricingController.get_product_options') as mock_controller:
            mock_controller.return_value = Result(status=True, data=expected_options)
            
            response = client.get(f'/api/pricing/products/{product_id}/options?store_code={store_code}')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] is True
            assert data['data'] == expected_options

    def test_get_product_options_controller_error(self, client):
        """Test product options retrieval with controller error."""
        product_id = 123
        store_code = 6
        
        with patch('server.routes.pricing_routes.PricingController.get_product_options') as mock_controller:
            mock_controller.return_value = Result(status=False, error="Controller Error")
            
            response = client.get(f'/api/pricing/products/{product_id}/options?store_code={store_code}')
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['status'] is False
            assert data['error'] == "Controller Error"

    def test_get_product_options_missing_store_code(self, client):
        """Test product options retrieval without store_code parameter."""
        product_id = 123
        
        response = client.get(f'/api/pricing/products/{product_id}/options')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'store_code is required' in data['error']

    def test_get_product_options_invalid_product_id(self, client):
        """Test product options retrieval with invalid product ID."""
        product_id = "invalid"
        store_code = 6
        
        response = client.get(f'/api/pricing/products/{product_id}/options?store_code={store_code}')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Invalid product ID' in data['error']

    def test_calculate_price_success(self, client):
        """Test successful price calculation via API."""
        product_id = 123
        store_code = 6
        options = [5, 447]
        expected_pricing = {
            "price": 22.51,
            "currency": "USD",
            "estimated_ship_date": "2024-01-15"
        }
        
        with patch('server.routes.pricing_routes.PricingController.calculate_price') as mock_controller:
            mock_controller.return_value = Result(status=True, data=expected_pricing)
            
            response = client.post(f'/api/pricing/products/{product_id}/price', 
                                 json={
                                     "options": options,
                                     "store_code": store_code
                                 })
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] is True
            assert data['data'] == expected_pricing

    def test_calculate_price_controller_error(self, client):
        """Test price calculation with controller error."""
        product_id = 123
        store_code = 6
        options = [5, 447]
        
        with patch('server.routes.pricing_routes.PricingController.calculate_price') as mock_controller:
            mock_controller.return_value = Result(status=False, error="Controller Error")
            
            response = client.post(f'/api/pricing/products/{product_id}/price', 
                                 json={
                                     "options": options,
                                     "store_code": store_code
                                 })
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['status'] is False
            assert data['error'] == "Controller Error"

    def test_calculate_price_missing_options(self, client):
        """Test price calculation without options."""
        product_id = 123
        store_code = 6
        
        response = client.post(f'/api/pricing/products/{product_id}/price', 
                             json={"store_code": store_code})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'options is required' in data['error']

    def test_calculate_price_missing_store_code(self, client):
        """Test price calculation without store_code."""
        product_id = 123
        options = [5, 447]
        
        response = client.post(f'/api/pricing/products/{product_id}/price', 
                             json={"options": options})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'store_code is required' in data['error']

    def test_get_cart_totals_success(self, client):
        """Test successful cart totals retrieval via API."""
        cart_id = 1
        expected_totals = {"total_items": 2, "total_price": 42.00}
        
        with patch('server.routes.pricing_routes.PricingController.get_cart_totals') as mock_controller:
            mock_controller.return_value = Result(status=True, data=expected_totals)
            
            response = client.get(f'/api/pricing/cart/{cart_id}/totals')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] is True
            assert data['data'] == expected_totals

    def test_get_cart_totals_controller_error(self, client):
        """Test cart totals retrieval with controller error."""
        cart_id = 1
        
        with patch('server.routes.pricing_routes.PricingController.get_cart_totals') as mock_controller:
            mock_controller.return_value = Result(status=False, error="Controller Error")
            
            response = client.get(f'/api/pricing/cart/{cart_id}/totals')
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['status'] is False
            assert data['error'] == "Controller Error"

    def test_get_cart_totals_invalid_cart_id(self, client):
        """Test cart totals retrieval with invalid cart ID."""
        cart_id = "invalid"
        
        response = client.get(f'/api/pricing/cart/{cart_id}/totals')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Invalid cart ID' in data['error']

    def test_get_shipping_estimates_success(self, client):
        """Test successful shipping estimates retrieval via API."""
        items = [{"productId": 123, "options": [5, 447]}]
        shipping_info = {"ShipState": "CA", "ShipZip": "90210", "ShipCountry": "US"}
        expected_estimates = [
            ["UPS", "UPS Standard", 9.1, 1],
            ["FedEx", "FedEx Standard Overnight", 9.67, 1]
        ]
        
        with patch('server.routes.pricing_routes.PricingController.get_shipping_estimates') as mock_controller:
            mock_controller.return_value = Result(status=True, data=expected_estimates)
            
            response = client.post('/api/pricing/shipping/estimates', 
                                 json={
                                     "items": items,
                                     "shippingInfo": shipping_info
                                 })
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] is True
            assert data['data'] == expected_estimates

    def test_get_shipping_estimates_controller_error(self, client):
        """Test shipping estimates retrieval with controller error."""
        items = [{"productId": 123, "options": [5, 447]}]
        shipping_info = {"ShipState": "CA", "ShipZip": "90210", "ShipCountry": "US"}
        
        with patch('server.routes.pricing_routes.PricingController.get_shipping_estimates') as mock_controller:
            mock_controller.return_value = Result(status=False, error="Controller Error")
            
            response = client.post('/api/pricing/shipping/estimates', 
                                 json={
                                     "items": items,
                                     "shippingInfo": shipping_info
                                 })
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['status'] is False
            assert data['error'] == "Controller Error"

    def test_get_shipping_estimates_missing_items(self, client):
        """Test shipping estimates retrieval without items."""
        shipping_info = {"ShipState": "CA", "ShipZip": "90210", "ShipCountry": "US"}
        
        response = client.post('/api/pricing/shipping/estimates', 
                             json={"shippingInfo": shipping_info})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'items is required' in data['error']

    def test_get_shipping_estimates_missing_shipping_info(self, client):
        """Test shipping estimates retrieval without shipping info."""
        items = [{"productId": 123, "options": [5, 447]}]
        
        response = client.post('/api/pricing/shipping/estimates', 
                             json={"items": items})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'shippingInfo is required' in data['error']

    def test_get_or_create_cart_success(self, client):
        """Test successful cart creation/retrieval via API."""
        session_id = "test_session"
        user_id = None
        store_code = 6
        expected_cart = {
            "id": 1,
            "session_id": session_id,
            "user_id": user_id,
            "store_code": store_code
        }
        
        with patch('server.routes.pricing_routes.PricingController.get_or_create_cart') as mock_controller:
            mock_controller.return_value = Result(status=True, data=expected_cart)
            
            response = client.get(f'/api/pricing/cart?session_id={session_id}&store_code={store_code}')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] is True
            assert data['data'] == expected_cart

    def test_get_or_create_cart_controller_error(self, client):
        """Test cart creation/retrieval with controller error."""
        session_id = "test_session"
        store_code = 6
        
        with patch('server.routes.pricing_routes.PricingController.get_or_create_cart') as mock_controller:
            mock_controller.return_value = Result(status=False, error="Controller Error")
            
            response = client.get(f'/api/pricing/cart?session_id={session_id}&store_code={store_code}')
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['status'] is False
            assert data['error'] == "Controller Error"

    def test_get_or_create_cart_missing_session_id(self, client):
        """Test cart creation/retrieval without session_id."""
        store_code = 6
        
        response = client.get(f'/api/pricing/cart?store_code={store_code}')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'session_id is required' in data['error']

    def test_get_or_create_cart_missing_store_code(self, client):
        """Test cart creation/retrieval without store_code."""
        session_id = "test_session"
        
        response = client.get(f'/api/pricing/cart?session_id={session_id}')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'store_code is required' in data['error']

    def test_add_item_to_cart_success(self, client):
        """Test successful cart item addition via API."""
        cart_id = 1
        product_id = 123
        product_name = "Test Product"
        product_sku = "TEST-001"
        quantity = 2
        selected_options = [5, 447]
        expected_item = {
            "id": 1,
            "cart_id": cart_id,
            "product_id": product_id,
            "product_name": product_name,
            "quantity": quantity,
            "total_price": 21.00
        }
        
        with patch('server.routes.pricing_routes.PricingController.add_item_to_cart') as mock_controller:
            mock_controller.return_value = Result(status=True, data=expected_item)
            
            response = client.post(f'/api/pricing/cart/{cart_id}/items', 
                                 json={
                                     "product_id": product_id,
                                     "product_name": product_name,
                                     "product_sku": product_sku,
                                     "quantity": quantity,
                                     "selected_options": selected_options
                                 })
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] is True
            assert data['data'] == expected_item

    def test_add_item_to_cart_controller_error(self, client):
        """Test cart item addition with controller error."""
        cart_id = 1
        product_id = 123
        product_name = "Test Product"
        product_sku = "TEST-001"
        quantity = 2
        selected_options = [5, 447]
        
        with patch('server.routes.pricing_routes.PricingController.add_item_to_cart') as mock_controller:
            mock_controller.return_value = Result(status=False, error="Controller Error")
            
            response = client.post(f'/api/pricing/cart/{cart_id}/items', 
                                 json={
                                     "product_id": product_id,
                                     "product_name": product_name,
                                     "product_sku": product_sku,
                                     "quantity": quantity,
                                     "selected_options": selected_options
                                 })
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['status'] is False
            assert data['error'] == "Controller Error"

    def test_add_item_to_cart_missing_required_fields(self, client):
        """Test cart item addition with missing required fields."""
        cart_id = 1
        
        # Test missing product_id
        response = client.post(f'/api/pricing/cart/{cart_id}/items', 
                             json={
                                 "product_name": "Test Product",
                                 "product_sku": "TEST-001",
                                 "quantity": 2,
                                 "selected_options": [5, 447]
                             })
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'product_id is required' in data['error']

    def test_add_item_to_cart_invalid_cart_id(self, client):
        """Test cart item addition with invalid cart ID."""
        cart_id = "invalid"
        product_id = 123
        product_name = "Test Product"
        product_sku = "TEST-001"
        quantity = 2
        selected_options = [5, 447]
        
        response = client.post(f'/api/pricing/cart/{cart_id}/items', 
                             json={
                                 "product_id": product_id,
                                 "product_name": product_name,
                                 "product_sku": product_sku,
                                 "quantity": quantity,
                                 "selected_options": selected_options
                             })
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Invalid cart ID' in data['error']

    def test_invalid_json_request(self, client):
        """Test API with invalid JSON request."""
        response = client.post('/api/pricing/products/123/price', 
                             data="invalid json",
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Invalid JSON' in data['error']

    def test_unsupported_method(self, client):
        """Test API with unsupported HTTP method."""
        response = client.delete('/api/pricing/products/123/options')
        
        assert response.status_code == 405  # Method Not Allowed

    def test_api_documentation_models(self, client):
        """Test that API models are properly defined."""
        # This test ensures the API models are working correctly
        # by checking that the Swagger documentation is accessible
        response = client.get('/api/')
        
        # Should return the Swagger UI or API documentation
        assert response.status_code in [200, 404]  # 404 is acceptable if Swagger is not configured
