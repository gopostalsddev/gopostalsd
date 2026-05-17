"""
Cart Routes for Go Postal SD Application

This module defines all cart-related API endpoints using Flask-RESTX.
It provides comprehensive cart management functionality.
"""

from flask import request
from flask_restx import Namespace, Resource, fields
from server.services.cart_service import CartService
from server.services.pricing_service import PricingService
from server.thirdparty.sinalite import SinaliteAdapter
from server.factories.main_factory import MainFactory
from server.middleware.auth_middleware import require_auth, require_cart_auth, get_user_id
import logging

logger = logging.getLogger(__name__)

# Create namespace for cart operations
api = Namespace('cart', description='Cart operations')

# Define models for API documentation
cart_item_model = api.model('CartItem', {
    'id': fields.Integer(description='Cart item ID'),
    'product_id': fields.Integer(description='Product ID'),
    'product_name': fields.String(description='Product name'),
    'product_sku': fields.String(description='Product SKU'),
    'quantity': fields.Integer(description='Quantity'),
    'unit_price': fields.Float(description='Unit price'),
    'total_price': fields.Float(description='Total price'),
    'selected_options': fields.Raw(description='Selected options'),
    'package_info': fields.Raw(description='Package information')
})

cart_model = api.model('Cart', {
    'id': fields.Integer(description='Cart ID'),
    'session_id': fields.String(description='Session ID'),
    'user_id': fields.Integer(description='User ID'),
    'store_code': fields.Integer(description='Store code'),
    'items': fields.List(fields.Nested(cart_item_model), description='Cart items'),
    'subtotal': fields.Float(description='Subtotal'),
    'shipping_cost': fields.Float(description='Shipping cost'),
    'tax_amount': fields.Float(description='Tax amount'),
    'total': fields.Float(description='Total amount'),
    'item_count': fields.Integer(description='Number of items'),
    'created_at': fields.String(description='Created timestamp'),
    'updated_at': fields.String(description='Updated timestamp')
})

add_to_cart_model = api.model('AddToCartRequest', {
    'product_id': fields.Integer(description='Product ID', required=True),
    'selected_options': fields.Raw(description='Selected product options', required=True),
    'quantity': fields.Integer(description='Quantity', default=1)
})

update_quantity_model = api.model('UpdateQuantityRequest', {
    'quantity': fields.Integer(description='New quantity', required=True)
})

shipping_address_model = api.model('ShippingAddress', {
    'street': fields.String(description='Street address', required=True),
    'city': fields.String(description='City', required=True),
    'state': fields.String(description='State/Province', required=True),
    'zip_code': fields.String(description='ZIP/Postal code', required=True),
    'country': fields.String(description='Country', required=True),
    'apt': fields.String(description='Apartment/Suite number')
})

shipping_option_model = api.model('ShippingOption', {
    'id': fields.Integer(description='Shipping option ID'),
    'carrier_name': fields.String(description='Carrier name'),
    'method_name': fields.String(description='Shipping method'),
    'price': fields.Float(description='Shipping cost'),
    'shipping_days': fields.Integer(description='Estimated shipping days')
})

# Create main factory instance
main_factory = MainFactory()

def get_cart_service():
    """Get cart service instance."""
    # Use the factory to get properly configured services
    sinalite_adapter = SinaliteAdapter()
    pricing_service = main_factory.get_pricing_service(sinalite_adapter)
    return main_factory.get_cart_service(pricing_service, sinalite_adapter)

# Define resources
@api.route('/')
@api.doc(security='Bearer')
class CartResource(Resource):
    """Resource for cart operations."""
    
    @require_auth
    @api.doc('get_cart')
    @api.marshal_with(cart_model)
    def get(self):
        """Get cart with items and totals."""
        session_id = request.args.get('session_id', 'default_session')
        
        cart_service = get_cart_service()
        result = cart_service.get_cart(session_id)
        
        if result['success']:
            return result['cart'], 200
        else:
            return {'error': result['error']}, 400

@api.route('/add')
@api.doc(security='Bearer')
class AddToCartResource(Resource):
    """Resource for adding items to cart."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    @api.doc('add_to_cart')
    # @api.expect(add_to_cart_model)  # Disabled - causing silent 400 errors
    # @api.marshal_with(cart_model)   # Disabled - causing silent 400 errors
    @require_cart_auth
    def post(self):
        """Add item to cart."""
        data = request.get_json()
        session_id = request.args.get('session_id', 'default_session')
        user_id = getattr(request, 'user_id', None)  # Get from decorator, not query params
        
        logger.info(f"Add to cart request - Session: {session_id}, User: {user_id}")
        
        if not data:
            error = {'error': 'Request body is required'}
            logger.warning(f"Add to cart failed: No request body")
            return error, 400
        
        # Validate required fields
        required_fields = ['product_id', 'selected_options']
        for field in required_fields:
            if field not in data:
                error = {'error': f'{field} is required'}
                logger.warning(f"Add to cart failed: Missing field '{field}'")
                return error, 400
        
        logger.info(f"Adding product {data['product_id']} to cart with options: {data['selected_options']}")
        
        cart_service = get_cart_service()
        result = cart_service.add_item_to_cart(
            session_id=session_id,
            product_id=data['product_id'],
            selected_options=data['selected_options'],
            quantity=data.get('quantity', 1),
            user_id=user_id
        )
        
        if result['success']:
            logger.info(f"Successfully added item to cart")
            return result['cart'], 201
        else:
            error = {'error': result['error']}
            logger.error(f"Failed to add item to cart: {result['error']}")
            return error, 400

@api.route('/items/<int:cart_item_id>/quantity')
@api.doc(security='Bearer')
class UpdateQuantityResource(Resource):
    """Resource for updating cart item quantity."""
    
    @require_auth
    @api.doc('update_quantity')
    @api.expect(update_quantity_model)
    @api.marshal_with(cart_model)
    def put(self, cart_item_id):
        """Update cart item quantity."""
        data = request.get_json()
        
        if not data or 'quantity' not in data:
            return {'error': 'Quantity is required'}, 400
        
        session_id = request.args.get('session_id', 'default_session')
        
        cart_service = get_cart_service()
        result = cart_service.update_cart_item_quantity(
            session_id=session_id,
            cart_item_id=cart_item_id,
            quantity=data['quantity']
        )
        
        if result['success']:
            return result['cart'], 200
        else:
            return {'error': result['error']}, 400

@api.route('/items/<int:cart_item_id>')
@api.doc(security='Bearer')
class RemoveItemResource(Resource):
    """Resource for removing items from cart."""
    
    @require_auth
    @api.doc('remove_from_cart')
    @api.marshal_with(cart_model)
    def delete(self, cart_item_id):
        """Remove item from cart."""
        session_id = request.args.get('session_id', 'default_session')
        
        cart_service = get_cart_service()
        result = cart_service.remove_cart_item(
            session_id=session_id,
            cart_item_id=cart_item_id
        )
        
        if result['success']:
            return result['cart'], 200
        else:
            return {'error': result['error']}, 400

@api.route('/clear')
@api.doc(security='Bearer')
class ClearCartResource(Resource):
    """Resource for clearing cart."""
    
    @require_auth
    @api.doc('clear_cart')
    def delete(self):
        """Clear all items from cart."""
        session_id = request.args.get('session_id', 'default_session')
        
        cart_service = get_cart_service()
        result = cart_service.clear_cart(session_id)
        
        if result['success']:
            return {'message': result['message']}, 200
        else:
            return {'error': result['error']}, 400

@api.route('/shipping')
@api.doc(security='Bearer')
class ShippingResource(Resource):
    """Resource for calculating shipping."""
    
    @require_auth
    @api.doc('calculate_shipping')
    @api.expect(shipping_address_model)
    @api.marshal_with(api.model('ShippingResponse', {
        'success': fields.Boolean(description='Success status'),
        'shipping_options': fields.List(fields.Nested(shipping_option_model), description='Available shipping options'),
        'error': fields.String(description='Error message')
    }))
    def post(self):
        """Calculate shipping options for cart."""
        data = request.get_json()
        
        if not data:
            return {'error': 'Request body is required'}, 400
        
        # Validate required fields
        required_fields = ['street', 'city', 'state', 'zip_code', 'country']
        for field in required_fields:
            if field not in data:
                return {'error': f'{field} is required'}, 400
        
        session_id = request.args.get('session_id', 'default_session')
        
        cart_service = get_cart_service()
        result = cart_service.calculate_shipping(
            session_id=session_id,
            destination_address=data
        )
        
        if result['success']:
            return {
                'success': True,
                'shipping_options': result['shipping_options']
            }, 200
        else:
            return {
                'success': False,
                'error': result['error']
            }, 400

@api.route('/summary')
@api.doc(security='Bearer')
class CartSummaryResource(Resource):
    """Resource for cart summary."""
    
    @require_auth
    @api.doc('get_cart_summary')
    @api.marshal_with(api.model('CartSummary', {
        'item_count': fields.Integer(description='Number of items'),
        'subtotal': fields.Float(description='Subtotal'),
        'shipping_cost': fields.Float(description='Shipping cost'),
        'tax_amount': fields.Float(description='Tax amount'),
        'total': fields.Float(description='Total amount'),
        'has_items': fields.Boolean(description='Whether cart has items')
    }))
    def get(self):
        """Get cart summary."""
        session_id = request.args.get('session_id', 'default_session')
        
        cart_service = get_cart_service()
        result = cart_service.get_cart(session_id)
        
        if result['success']:
            cart = result['cart']
            return {
                'item_count': cart.get('item_count', 0),
                'subtotal': cart.get('subtotal', 0),
                'shipping_cost': cart.get('shipping_cost', 0),
                'tax_amount': cart.get('tax_amount', 0),
                'total': cart.get('total', 0),
                'has_items': cart.get('item_count', 0) > 0
            }, 200
        else:
            return {
                'item_count': 0,
                'subtotal': 0,
                'shipping_cost': 0,
                'tax_amount': 0,
                'total': 0,
                'has_items': False
            }, 200