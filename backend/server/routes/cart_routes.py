"""
Cart Routes for Go Postal SD Application

This module defines all cart-related API endpoints using Flask-RESTX.
It follows the same pattern as other route modules for consistency.
"""

from flask import request
from flask_restx import Namespace, Resource, fields
from server.controllers.cart_controller import CartController

# Create namespace for cart operations
api = Namespace('cart', description='Cart operations')

# Define models for API documentation
cart_model = api.model('Cart', {
    'cart_id': fields.Integer(description='Cart ID'),
    'session_id': fields.String(description='Session ID'),
    'user_id': fields.Integer(description='User ID'),
    'store_code': fields.Integer(description='Store code'),
    'created_at': fields.DateTime(description='Created timestamp'),
    'updated_at': fields.DateTime(description='Updated timestamp')
})

cart_item_model = api.model('CartItem', {
    'cart_item_id': fields.Integer(description='Cart item ID'),
    'cart_id': fields.Integer(description='Cart ID'),
    'product_id': fields.Integer(description='Product ID'),
    'product_name': fields.String(description='Product name'),
    'product_sku': fields.String(description='Product SKU'),
    'selected_options': fields.List(fields.Integer, description='Selected option IDs'),
    'quantity': fields.Integer(description='Quantity'),
    'unit_price': fields.Float(description='Unit price'),
    'total_price': fields.Float(description='Total price'),
    'created_at': fields.DateTime(description='Created timestamp'),
    'updated_at': fields.DateTime(description='Updated timestamp')
})

cart_totals_model = api.model('CartTotals', {
    'subtotal': fields.Float(description='Subtotal'),
    'tax': fields.Float(description='Tax amount'),
    'total': fields.Float(description='Total amount'),
    'item_count': fields.Integer(description='Number of items')
})

add_to_cart_model = api.model('AddToCartRequest', {
    'product_id': fields.Integer(description='Product ID', required=True),
    'product_name': fields.String(description='Product name', required=True),
    'product_sku': fields.String(description='Product SKU', required=True),
    'selected_options': fields.List(fields.Integer, description='Selected option IDs', required=True),
    'quantity': fields.Integer(description='Quantity', default=1)
})

# Define resources
@api.route('/')
class CartResource(Resource):
    """Resource for cart operations."""
    
    @api.doc('get_or_create_cart')
    @api.marshal_with(cart_model)
    def get(self):
        """Get or create a cart."""
        session_id = request.args.get('session_id', 'default_session')
        user_id = request.args.get('user_id', type=int)
        store_code = request.args.get('store_code', 6, type=int)
        
        result = CartController.get_or_create_cart(session_id, user_id, store_code)
        
        if result.status:
            return result.data, 200
        else:
            return {'error': result.error}, 400

@api.route('/<int:cart_id>/items')
class CartItemsResource(Resource):
    """Resource for cart item operations."""
    
    @api.doc('add_item_to_cart')
    @api.expect(add_to_cart_model)
    @api.marshal_with(cart_item_model)
    def post(self, cart_id):
        """Add an item to the cart."""
        data = request.get_json()
        
        result = CartController.add_item_to_cart(
            cart_id=cart_id,
            product_id=data['product_id'],
            product_name=data['product_name'],
            product_sku=data['product_sku'],
            selected_options=data['selected_options'],
            quantity=data.get('quantity', 1)
        )
        
        if result.status:
            return result.data, 201
        else:
            return {'error': result.error}, 400

@api.route('/<int:cart_id>/totals')
class CartTotalsResource(Resource):
    """Resource for cart totals."""
    
    @api.doc('get_cart_totals')
    @api.marshal_with(cart_totals_model)
    def get(self, cart_id):
        """Get cart totals."""
        result = CartController.get_cart_totals(cart_id)
        
        if result.status:
            return result.data, 200
        else:
            return {'error': result.error}, 400
