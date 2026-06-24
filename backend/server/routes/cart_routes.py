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
from server.validation.input_validator import (
    validate_address_input,
    validate_number_input,
    validate_string_input,
)
from server.routes.response_utils import error_response
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


def _get_required_session_id():
    """Require and validate a session_id query parameter."""
    session_id = request.args.get('session_id')
    if not session_id:
        return None, error_response('session_id is required', 400)

    session_result = validate_string_input(session_id, max_length=255)
    if not session_result.is_valid:
        return None, error_response('Invalid session_id', 400)

    return str(session_id), None

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
    @api.response(200, 'Cart fetched successfully', cart_model)
    def get(self):
        """Get cart with items and totals."""
        session_id, session_error = _get_required_session_id()
        if session_error:
            return session_error
        
        cart_service = get_cart_service()
        result = cart_service.get_cart(session_id)
        
        if result['success']:
            return result['cart'], 200
        else:
            return error_response(result['error'], 400, code='CART_FETCH_ERROR', category='business_logic')

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
        data = request.get_json(silent=True)
        session_id, session_error = _get_required_session_id()
        if session_error:
            return session_error
        user_id = getattr(request, 'user_id', None)  # Get from decorator, not query params
        
        logger.info(f"Add to cart request - Session: {session_id}, User: {user_id}")
        
        if not data:
            logger.warning(f"Add to cart failed: No request body")
            return error_response('Request body is required', 400)

        # Validate required fields
        required_fields = ['product_id', 'selected_options']
        for field in required_fields:
            if field not in data:
                logger.warning(f"Add to cart failed: Missing field '{field}'")
                return error_response(f'{field} is required', 400)

        product_id_result = validate_number_input(data.get('product_id'), min_value=1, integer_only=True)
        if not product_id_result.is_valid:
            return error_response('Invalid product_id', 400)

        quantity_result = validate_number_input(data.get('quantity', 1), min_value=1, max_value=100, integer_only=True)
        if not quantity_result.is_valid:
            return error_response('Invalid quantity', 400)

        selected_options = data.get('selected_options')
        if not isinstance(selected_options, list):
            return error_response('selected_options must be a list', 400)

        sanitized_options = []
        for option in selected_options:
            option_result = validate_number_input(option, min_value=1, integer_only=True)
            if not option_result.is_valid:
                return error_response('selected_options must contain positive integers', 400)
            sanitized_options.append(int(option_result.sanitized_data))
        
        logger.info(f"Adding product {product_id_result.sanitized_data} to cart with options: {sanitized_options}")
        
        cart_service = get_cart_service()
        result = cart_service.add_item_to_cart(
            session_id=session_id,
            product_id=int(product_id_result.sanitized_data),
            selected_options=sanitized_options,
            quantity=int(quantity_result.sanitized_data),
            user_id=user_id
        )
        
        if result['success']:
            logger.info(f"Successfully added item to cart")
            return result['cart'], 201
        else:
            logger.error("Failed to add item to cart: %s", result['error'])
            return error_response(result['error'], 400, code='CART_ADD_ITEM_ERROR', category='business_logic')

@api.route('/items/<int:cart_item_id>/quantity')
@api.doc(security='Bearer')
class UpdateQuantityResource(Resource):
    """Resource for updating cart item quantity."""
    
    @require_auth
    @api.doc('update_quantity')
    @api.expect(update_quantity_model)
    @api.response(200, 'Cart item quantity updated', cart_model)
    def put(self, cart_item_id):
        """Update cart item quantity."""
        data = request.get_json(silent=True)
        
        if not data or 'quantity' not in data:
            return error_response('Quantity is required', 400)

        quantity_result = validate_number_input(data['quantity'], min_value=0, max_value=100, integer_only=True)
        if not quantity_result.is_valid:
            return error_response('Invalid quantity', 400)
        
        session_id, session_error = _get_required_session_id()
        if session_error:
            return session_error
        
        cart_service = get_cart_service()
        result = cart_service.update_cart_item_quantity(
            session_id=session_id,
            cart_item_id=cart_item_id,
            quantity=int(quantity_result.sanitized_data)
        )
        
        if result['success']:
            return result['cart'], 200
        else:
            return error_response(result['error'], 400, code='CART_UPDATE_ITEM_ERROR', category='business_logic')

@api.route('/items/<int:cart_item_id>')
@api.doc(security='Bearer')
class RemoveItemResource(Resource):
    """Resource for removing items from cart."""
    
    @require_auth
    @api.doc('remove_from_cart')
    @api.response(200, 'Cart item removed', cart_model)
    def delete(self, cart_item_id):
        """Remove item from cart."""
        session_id, session_error = _get_required_session_id()
        if session_error:
            return session_error
        
        cart_service = get_cart_service()
        result = cart_service.remove_cart_item(
            session_id=session_id,
            cart_item_id=cart_item_id
        )
        
        if result['success']:
            return result['cart'], 200
        else:
            return error_response(result['error'], 400, code='CART_REMOVE_ITEM_ERROR', category='business_logic')

@api.route('/clear')
@api.doc(security='Bearer')
class ClearCartResource(Resource):
    """Resource for clearing cart."""
    
    @require_auth
    @api.doc('clear_cart')
    def delete(self):
        """Clear all items from cart."""
        session_id, session_error = _get_required_session_id()
        if session_error:
            return session_error
        
        cart_service = get_cart_service()
        result = cart_service.clear_cart(session_id)
        
        if result['success']:
            return {'message': result['message']}, 200
        else:
            return error_response(result['error'], 400, code='CART_CLEAR_ERROR', category='business_logic')

@api.route('/shipping')
@api.doc(security='Bearer')
class ShippingResource(Resource):
    """Resource for calculating shipping."""
    
    @require_auth
    @api.doc('calculate_shipping')
    @api.expect(shipping_address_model)
    @api.response(200, 'Shipping options calculated successfully')
    def post(self):
        """Calculate shipping options for cart."""
        data = request.get_json(silent=True)
        
        if not data:
            return error_response('Request body is required', 400)
        
        # Validate required fields
        address_result = validate_address_input(data)
        if not address_result.is_valid:
            return error_response('Invalid shipping address', 400)
        
        session_id, session_error = _get_required_session_id()
        if session_error:
            return session_error
        
        cart_service = get_cart_service()
        result = cart_service.calculate_shipping(
            session_id=session_id,
            destination_address=address_result.sanitized_data
        )
        
        if result['success']:
            return {
                'success': True,
                'shipping_options': result['shipping_options']
            }, 200
        else:
            return error_response(result['error'], 400, code='SHIPPING_CALCULATION_ERROR', category='business_logic')

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
        session_id, session_error = _get_required_session_id()
        if session_error:
            return session_error
        
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