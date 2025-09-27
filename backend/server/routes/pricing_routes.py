"""
Pricing Routes for Go Postal SD Application

This module defines all pricing-related API endpoints using Flask-RESTX.
It follows the same pattern as print_product_routes.py.
"""

from flask_restx import Namespace, Resource, fields
from flask import request
from server.controllers.pricing_controller import PricingController

# Define a namespace for pricing
api = Namespace("Pricing", description="Operations related to product pricing and shipping")

# Define request/response models
product_options_model = api.model("ProductOptions", {
    "group": fields.String(description="Option group name"),
    "options": fields.List(fields.Nested(api.model("Option", {
        "id": fields.Integer(description="Option ID"),
        "name": fields.String(description="Option name")
    })), description="Available options for this group")
})

pricing_request_model = api.model("PricingRequest", {
    "options": fields.List(fields.Integer, description="Selected option IDs"),
    "store_code": fields.Integer(description="Store code (6 for Canada, 9 for US)", default=6)
})

pricing_response_model = api.model("PricingResponse", {
    "price": fields.Float(description="Product price"),
    "currency": fields.String(description="Currency code"),
    "estimated_ship_date": fields.String(description="Estimated ship date")
})

shipping_estimate_model = api.model("ShippingEstimateRequest", {
    "items": fields.List(fields.Nested(api.model("CartItem", {
        "productId": fields.Integer(description="Product ID"),
        "options": fields.Raw(description="Selected options")
    })), description="Cart items"),
    "shippingInfo": fields.Nested(api.model("ShippingInfo", {
        "ShipState": fields.String(description="State/Province code"),
        "ShipZip": fields.String(description="ZIP/Postal code"),
        "ShipCountry": fields.String(description="Country code")
    }), description="Shipping destination information")
})

shipping_option_model = api.model("ShippingOption", {
    "carrier_name": fields.String(description="Carrier name"),
    "method_name": fields.String(description="Shipping method name"),
    "price": fields.Float(description="Shipping price"),
    "shipping_days": fields.Integer(description="Delivery days")
})

cart_totals_model = api.model("CartTotals", {
    "subtotal": fields.Float(description="Subtotal amount"),
    "tax": fields.Float(description="Tax amount"),
    "total": fields.Float(description="Total amount"),
    "item_count": fields.Integer(description="Number of items in cart")
})

cart_model = api.model("Cart", {
    "id": fields.Integer(description="Cart ID"),
    "session_id": fields.String(description="Session identifier"),
    "user_id": fields.Integer(description="User ID"),
    "store_code": fields.Integer(description="Store code"),
    "created_at": fields.DateTime(description="Created timestamp"),
    "updated_at": fields.DateTime(description="Updated timestamp")
})

cart_item_model = api.model("CartItem", {
    "id": fields.Integer(description="Cart item ID"),
    "cart_id": fields.Integer(description="Cart ID"),
    "product_id": fields.Integer(description="Product ID"),
    "product_name": fields.String(description="Product name"),
    "product_sku": fields.String(description="Product SKU"),
    "quantity": fields.Integer(description="Quantity"),
    "unit_price": fields.Float(description="Unit price"),
    "total_price": fields.Float(description="Total price"),
    "created_at": fields.DateTime(description="Created timestamp"),
    "updated_at": fields.DateTime(description="Updated timestamp")
})

add_to_cart_model = api.model("AddToCartRequest", {
    "product_id": fields.Integer(description="Product ID", required=True),
    "product_name": fields.String(description="Product name", required=True),
    "product_sku": fields.String(description="Product SKU", required=True),
    "selected_options": fields.List(fields.Integer, description="Selected option IDs", required=True),
    "quantity": fields.Integer(description="Quantity", default=1)
})

# API Resources
@api.route('/products/<int:product_id>/options')
class ProductOptionsResource(Resource):
    """Resource for getting product options."""
    
    @api.doc('get_product_options')
    @api.param('store_code', 'Store code (6 for Canada, 9 for US)', type='int', default=6)
    @api.marshal_with(product_options_model, as_list=True)
    def get(self, product_id):
        """Get available options for a product."""
        store_code = request.args.get('store_code', 6, type=int)
        
        result = PricingController.get_product_options(product_id, store_code)
        
        if result.status:
            return result.data['options']
        else:
            return {'error': result.error}, 400


@api.route('/products/<int:product_id>/price')
class ProductPriceResource(Resource):
    """Resource for calculating product prices."""
    
    @api.doc('calculate_product_price')
    @api.expect(pricing_request_model)
    @api.marshal_with(pricing_response_model)
    def post(self, product_id):
        """Calculate price for a product with selected options."""
        data = request.get_json()
        
        if not data:
            return {'error': 'Request body is required'}, 400
        
        options = data.get('options', [])
        store_code = data.get('store_code', 6)
        
        result = PricingController.calculate_price(product_id, options, store_code)
        
        if result.status:
            return result.data
        else:
            return {'error': result.error}, 400


@api.route('/cart/<int:cart_id>/totals')
class CartTotalsResource(Resource):
    """Resource for getting cart totals."""
    
    @api.doc('get_cart_totals')
    @api.marshal_with(cart_totals_model)
    def get(self, cart_id):
        """Get cart totals including subtotal, tax, and total."""
        result = PricingController.get_cart_totals(cart_id)
        
        if result.status:
            return result.data
        else:
            return {'error': result.error}, 400


@api.route('/cart')
class CartResource(Resource):
    """Resource for cart operations."""
    
    @api.doc('get_or_create_cart')
    @api.param('session_id', 'Session identifier', required=True)
    @api.param('user_id', 'User ID for logged-in users', type='int')
    @api.param('store_code', 'Store code (6 for Canada, 9 for US)', type='int', default=6)
    @api.marshal_with(cart_model)
    def get(self):
        """Get or create a cart."""
        session_id = request.args.get('session_id')
        user_id = request.args.get('user_id', type=int)
        store_code = request.args.get('store_code', 6, type=int)
        
        if not session_id:
            return {'error': 'session_id is required'}, 400
        
        result = PricingController.get_or_create_cart(session_id, user_id, store_code)
        
        if result.status:
            return result.data
        else:
            return {'error': result.error}, 400


@api.route('/cart/<int:cart_id>/items')
class CartItemsResource(Resource):
    """Resource for cart items."""
    
    @api.doc('add_item_to_cart')
    @api.expect(add_to_cart_model)
    @api.marshal_with(cart_item_model)
    def post(self, cart_id):
        """Add item to cart."""
        data = request.get_json()
        
        if not data:
            return {'error': 'Request body is required'}, 400
        
        product_id = data.get('product_id')
        product_name = data.get('product_name')
        product_sku = data.get('product_sku')
        selected_options = data.get('selected_options', [])
        quantity = data.get('quantity', 1)
        
        if not all([product_id, product_name, product_sku]):
            return {'error': 'product_id, product_name, and product_sku are required'}, 400
        
        result = PricingController.add_item_to_cart(
            cart_id, product_id, product_name, product_sku, selected_options, quantity
        )
        
        if result.status:
            return result.data
        else:
            return {'error': result.error}, 400


@api.route('/shipping/estimates')
class ShippingEstimatesResource(Resource):
    """Resource for shipping estimates."""
    
    @api.doc('get_shipping_estimates')
    @api.expect(shipping_estimate_model)
    @api.marshal_with(shipping_option_model, as_list=True)
    def post(self):
        """Get shipping estimates for cart items."""
        data = request.get_json()
        
        if not data:
            return {'error': 'Request body is required'}, 400
        
        items = data.get('items', [])
        shipping_info = data.get('shippingInfo', data.get('shipping_info', {}))
        
        if not items or not shipping_info:
            return {'error': 'items and shippingInfo are required'}, 400
        
        result = PricingController.get_shipping_estimates(items, shipping_info)
        
        if result.status:
            return result.data['shipping_options']
        else:
            return {'error': result.error}, 400


# Note: The api namespace is exported directly and registered in routes/__init__.py
# This follows the same pattern as print_product_routes.py