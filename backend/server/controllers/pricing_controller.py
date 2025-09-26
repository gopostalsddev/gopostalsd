"""
Pricing Controller for Go Postal SD Application

This controller handles HTTP requests related to product pricing, cart management,
and shipping calculations. It provides a clean REST API interface for the frontend.
"""

from flask import request, jsonify
from flask_restx import Resource, Namespace, fields
from typing import Dict, List, Optional
import logging
from server import database as db
from server.services.pricing_service import PricingService, CartService
from server.models.pricing import StoreCode
from server.thirdparty.sinalite import SinaliteAdapter

logger = logging.getLogger(__name__)

# Create namespace for pricing-related endpoints
pricing_ns = Namespace('pricing', description='Product pricing and cart operations')

# Request/Response models for API documentation
product_options_model = pricing_ns.model('ProductOptions', {
    'group': fields.String(required=True, description='Option group name'),
    'options': fields.List(fields.Raw, description='List of options in this group')
})

pricing_request_model = pricing_ns.model('PricingRequest', {
    'product_id': fields.Integer(required=True, description='Sinalite product ID'),
    'options': fields.List(fields.Integer, required=True, description='Selected option IDs'),
    'store_code': fields.Integer(required=True, description='Store code (6 for Canada, 9 for US)')
})

pricing_response_model = pricing_ns.model('PricingResponse', {
    'price': fields.String(description='Product price'),
    'package_info': fields.Raw(description='Package information'),
    'product_options': fields.Raw(description='Selected product options')
})

cart_item_model = pricing_ns.model('CartItem', {
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

cart_model = pricing_ns.model('Cart', {
    'id': fields.Integer(description='Cart ID'),
    'session_id': fields.String(description='Session ID'),
    'store_code': fields.Integer(description='Store code'),
    'items': fields.List(fields.Nested(cart_item_model), description='Cart items'),
    'totals': fields.Raw(description='Cart totals')
})

add_to_cart_model = pricing_ns.model('AddToCartRequest', {
    'product_id': fields.Integer(required=True, description='Sinalite product ID'),
    'product_name': fields.String(required=True, description='Product name'),
    'product_sku': fields.String(description='Product SKU'),
    'selected_options': fields.List(fields.Integer, required=True, description='Selected option IDs'),
    'quantity': fields.Integer(required=True, description='Quantity to add', default=1)
})

shipping_estimate_model = pricing_ns.model('ShippingEstimateRequest', {
    'items': fields.List(fields.Raw, required=True, description='Cart items'),
    'shipping_info': fields.Raw(required=True, description='Shipping destination info')
})

shipping_option_model = pricing_ns.model('ShippingOption', {
    'carrier_name': fields.String(description='Carrier name'),
    'method_name': fields.String(description='Shipping method name'),
    'price': fields.Float(description='Shipping price'),
    'shipping_days': fields.Integer(description='Delivery days')
})


class PricingController:
    """
    Controller for handling pricing-related operations.
    Implements the Controller pattern for clean separation of concerns.
    """
    
    def __init__(self, sinalite_adapter: SinaliteAdapter, pricing_service: PricingService, cart_service: CartService):
        self.sinalite_adapter = sinalite_adapter
        self.pricing_service = pricing_service
        self.cart_service = cart_service
    
    def get_product_options(self, product_id: int, store_code: int) -> Dict:
        """
        Get available options for a product.
        
        Args:
            product_id: Sinalite product ID
            store_code: Store code (6 for Canada, 9 for US)
            
        Returns:
            Dict containing grouped product options
        """
        try:
            options = self.pricing_service.get_product_options(product_id, store_code)
            
            return {
                'success': True,
                'data': {
                    'product_id': product_id,
                    'store_code': store_code,
                    'options': options
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting product options: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to retrieve product options',
                'details': str(e)
            }
    
    def calculate_price(self, product_id: int, options: List[int], store_code: int) -> Dict:
        """
        Calculate price for a product with selected options.
        
        Args:
            product_id: Sinalite product ID
            options: List of selected option IDs
            store_code: Store code (6 for Canada, 9 for US)
            
        Returns:
            Dict containing pricing information
        """
        try:
            pricing = self.pricing_service.calculate_product_price(product_id, options, store_code)
            
            if not pricing:
                return {
                    'success': False,
                    'error': 'Could not calculate price for the selected options'
                }
            
            return {
                'success': True,
                'data': pricing
            }
            
        except Exception as e:
            logger.error(f"Error calculating price: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to calculate price',
                'details': str(e)
            }
    
    def get_product_variants(self, product_id: int, offset: int = 0) -> Dict:
        """
        Get product variants with pricing.
        
        Args:
            product_id: Sinalite product ID
            offset: Pagination offset
            
        Returns:
            Dict containing product variants
        """
        try:
            variants = self.pricing_service.get_product_variants(product_id, offset)
            
            return {
                'success': True,
                'data': {
                    'product_id': product_id,
                    'variants': variants,
                    'count': len(variants)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting product variants: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to retrieve product variants',
                'details': str(e)
            }
    
    def get_or_create_cart(self, session_id: str, user_id: Optional[int] = None, 
                          store_code: int = StoreCode.CANADA.value) -> Dict:
        """
        Get existing cart or create a new one.
        
        Args:
            session_id: Session identifier
            user_id: Optional user ID for logged-in users
            store_code: Store code (6 for Canada, 9 for US)
            
        Returns:
            Dict containing cart information
        """
        try:
            cart = self.cart_service.get_or_create_cart(session_id, user_id, store_code)
            cart_data = cart.to_dict()
            
            # Add totals
            totals = self.cart_service.get_cart_total(cart.id)
            cart_data['totals'] = totals
            
            return {
                'success': True,
                'data': cart_data
            }
            
        except Exception as e:
            logger.error(f"Error getting/creating cart: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to get or create cart',
                'details': str(e)
            }
    
    def add_item_to_cart(self, cart_id: int, product_id: int, product_name: str,
                        product_sku: str, selected_options: List[int], 
                        quantity: int = 1) -> Dict:
        """
        Add item to cart.
        
        Args:
            cart_id: Cart ID
            product_id: Sinalite product ID
            product_name: Product name
            product_sku: Product SKU
            selected_options: List of selected option IDs
            quantity: Quantity to add
            
        Returns:
            Dict containing cart item information
        """
        try:
            cart_item = self.cart_service.add_item_to_cart(
                cart_id, product_id, product_name, product_sku, 
                selected_options, quantity
            )
            
            if not cart_item:
                return {
                    'success': False,
                    'error': 'Failed to add item to cart'
                }
            
            return {
                'success': True,
                'data': cart_item.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error adding item to cart: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to add item to cart',
                'details': str(e)
            }
    
    def update_cart_item_quantity(self, cart_item_id: int, quantity: int) -> Dict:
        """
        Update cart item quantity.
        
        Args:
            cart_item_id: Cart item ID
            quantity: New quantity
            
        Returns:
            Dict indicating success or failure
        """
        try:
            success = self.cart_service.update_cart_item_quantity(cart_item_id, quantity)
            
            if not success:
                return {
                    'success': False,
                    'error': 'Failed to update cart item quantity'
                }
            
            return {
                'success': True,
                'message': 'Cart item quantity updated successfully'
            }
            
        except Exception as e:
            logger.error(f"Error updating cart item quantity: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to update cart item quantity',
                'details': str(e)
            }
    
    def remove_cart_item(self, cart_item_id: int) -> Dict:
        """
        Remove item from cart.
        
        Args:
            cart_item_id: Cart item ID
            
        Returns:
            Dict indicating success or failure
        """
        try:
            success = self.cart_service.remove_cart_item(cart_item_id)
            
            if not success:
                return {
                    'success': False,
                    'error': 'Failed to remove cart item'
                }
            
            return {
                'success': True,
                'message': 'Cart item removed successfully'
            }
            
        except Exception as e:
            logger.error(f"Error removing cart item: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to remove cart item',
                'details': str(e)
            }
    
    def get_cart_totals(self, cart_id: int) -> Dict:
        """
        Get cart totals.
        
        Args:
            cart_id: Cart ID
            
        Returns:
            Dict containing cart totals
        """
        try:
            totals = self.cart_service.get_cart_total(cart_id)
            
            return {
                'success': True,
                'data': totals
            }
            
        except Exception as e:
            logger.error(f"Error getting cart totals: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to get cart totals',
                'details': str(e)
            }
    
    def get_shipping_estimates(self, items: List[Dict], shipping_info: Dict) -> Dict:
        """
        Get shipping estimates for cart items.
        
        Args:
            items: List of cart items
            shipping_info: Shipping destination information
            
        Returns:
            Dict containing available shipping options
        """
        try:
            estimates = self.pricing_service.get_shipping_estimates(items, shipping_info)
            
            return {
                'success': True,
                'data': {
                    'shipping_options': estimates,
                    'count': len(estimates)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting shipping estimates: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to get shipping estimates',
                'details': str(e)
            }


# API Resource classes for Flask-RESTX
@pricing_ns.route('/products/<int:product_id>/options')
class ProductOptionsResource(Resource):
    """Resource for getting product options."""
    
    @pricing_ns.doc('get_product_options')
    @pricing_ns.param('store_code', 'Store code (6 for Canada, 9 for US)', type='int', default=6)
    @pricing_ns.marshal_with(product_options_model, as_list=True)
    def get(self, product_id):
        """Get available options for a product."""
        store_code = request.args.get('store_code', 6, type=int)
        
        # Get pricing controller from app context
        from flask import current_app
        pricing_controller = current_app.extensions.get('pricing_controller')
        
        if not pricing_controller:
            return {'success': False, 'error': 'Pricing service not available'}, 500
        
        result = pricing_controller.get_product_options(product_id, store_code)
        
        if result['success']:
            return result['data']['options']
        else:
            return {'error': result['error']}, 400


@pricing_ns.route('/products/<int:product_id>/price')
class ProductPriceResource(Resource):
    """Resource for calculating product prices."""
    
    @pricing_ns.doc('calculate_product_price')
    @pricing_ns.expect(pricing_request_model)
    @pricing_ns.marshal_with(pricing_response_model)
    def post(self, product_id):
        """Calculate price for a product with selected options."""
        data = request.get_json()
        
        if not data:
            return {'error': 'Request body is required'}, 400
        
        options = data.get('options', [])
        store_code = data.get('store_code', 6)
        
        # Get pricing controller from app context
        from flask import current_app
        pricing_controller = current_app.extensions.get('pricing_controller')
        
        if not pricing_controller:
            return {'error': 'Pricing service not available'}, 500
        
        result = pricing_controller.calculate_price(product_id, options, store_code)
        
        if result['success']:
            return result['data']
        else:
            return {'error': result['error']}, 400


@pricing_ns.route('/products/<int:product_id>/variants')
class ProductVariantsResource(Resource):
    """Resource for getting product variants."""
    
    @pricing_ns.doc('get_product_variants')
    @pricing_ns.param('offset', 'Pagination offset', type='int', default=0)
    def get(self, product_id):
        """Get product variants with pricing."""
        offset = request.args.get('offset', 0, type=int)
        
        # Get pricing controller from app context
        from flask import current_app
        pricing_controller = current_app.extensions.get('pricing_controller')
        
        if not pricing_controller:
            return {'error': 'Pricing service not available'}, 500
        
        result = pricing_controller.get_product_variants(product_id, offset)
        
        if result['success']:
            return result['data']
        else:
            return {'error': result['error']}, 400


@pricing_ns.route('/cart')
class CartResource(Resource):
    """Resource for cart operations."""
    
    @pricing_ns.doc('get_or_create_cart')
    @pricing_ns.param('session_id', 'Session identifier', required=True)
    @pricing_ns.param('user_id', 'User ID (optional)', type='int')
    @pricing_ns.param('store_code', 'Store code (6 for Canada, 9 for US)', type='int', default=6)
    @pricing_ns.marshal_with(cart_model)
    def get(self):
        """Get or create a cart."""
        session_id = request.args.get('session_id')
        user_id = request.args.get('user_id', type=int)
        store_code = request.args.get('store_code', 6, type=int)
        
        if not session_id:
            return {'error': 'session_id is required'}, 400
        
        # Get pricing controller from app context
        from flask import current_app
        pricing_controller = current_app.extensions.get('pricing_controller')
        
        if not pricing_controller:
            return {'error': 'Pricing service not available'}, 500
        
        result = pricing_controller.get_or_create_cart(session_id, user_id, store_code)
        
        if result['success']:
            return result['data']
        else:
            return {'error': result['error']}, 400


@pricing_ns.route('/cart/<int:cart_id>/items')
class CartItemsResource(Resource):
    """Resource for cart item operations."""
    
    @pricing_ns.doc('add_item_to_cart')
    @pricing_ns.expect(add_to_cart_model)
    @pricing_ns.marshal_with(cart_item_model)
    def post(self, cart_id):
        """Add item to cart."""
        data = request.get_json()
        
        if not data:
            return {'error': 'Request body is required'}, 400
        
        product_id = data.get('product_id')
        product_name = data.get('product_name')
        product_sku = data.get('product_sku', '')
        selected_options = data.get('selected_options', [])
        quantity = data.get('quantity', 1)
        
        if not all([product_id, product_name, selected_options]):
            return {'error': 'product_id, product_name, and selected_options are required'}, 400
        
        # Get pricing controller from app context
        from flask import current_app
        pricing_controller = current_app.extensions.get('pricing_controller')
        
        if not pricing_controller:
            return {'error': 'Pricing service not available'}, 500
        
        result = pricing_controller.add_item_to_cart(
            cart_id, product_id, product_name, product_sku, 
            selected_options, quantity
        )
        
        if result['success']:
            return result['data']
        else:
            return {'error': result['error']}, 400


@pricing_ns.route('/cart/items/<int:cart_item_id>')
class CartItemResource(Resource):
    """Resource for individual cart item operations."""
    
    @pricing_ns.doc('update_cart_item_quantity')
    @pricing_ns.param('quantity', 'New quantity', type='int', required=True)
    def put(self, cart_item_id):
        """Update cart item quantity."""
        quantity = request.args.get('quantity', type=int)
        
        if quantity is None:
            return {'error': 'quantity parameter is required'}, 400
        
        # Get pricing controller from app context
        from flask import current_app
        pricing_controller = current_app.extensions.get('pricing_controller')
        
        if not pricing_controller:
            return {'error': 'Pricing service not available'}, 500
        
        result = pricing_controller.update_cart_item_quantity(cart_item_id, quantity)
        
        if result['success']:
            return result
        else:
            return {'error': result['error']}, 400
    
    @pricing_ns.doc('remove_cart_item')
    def delete(self, cart_item_id):
        """Remove item from cart."""
        # Get pricing controller from app context
        from flask import current_app
        pricing_controller = current_app.extensions.get('pricing_controller')
        
        if not pricing_controller:
            return {'error': 'Pricing service not available'}, 500
        
        result = pricing_controller.remove_cart_item(cart_item_id)
        
        if result['success']:
            return result
        else:
            return {'error': result['error']}, 400


@pricing_ns.route('/cart/<int:cart_id>/totals')
class CartTotalsResource(Resource):
    """Resource for cart totals."""
    
    @pricing_ns.doc('get_cart_totals')
    def get(self, cart_id):
        """Get cart totals."""
        # Get pricing controller from app context
        from flask import current_app
        pricing_controller = current_app.extensions.get('pricing_controller')
        
        if not pricing_controller:
            return {'error': 'Pricing service not available'}, 500
        
        result = pricing_controller.get_cart_totals(cart_id)
        
        if result['success']:
            return result['data']
        else:
            return {'error': result['error']}, 400


@pricing_ns.route('/shipping/estimates')
class ShippingEstimatesResource(Resource):
    """Resource for shipping estimates."""
    
    @pricing_ns.doc('get_shipping_estimates')
    @pricing_ns.expect(shipping_estimate_model)
    @pricing_ns.marshal_with(shipping_option_model, as_list=True)
    def post(self):
        """Get shipping estimates for cart items."""
        data = request.get_json()
        
        if not data:
            return {'error': 'Request body is required'}, 400
        
        items = data.get('items', [])
        shipping_info = data.get('shipping_info', {})
        
        if not items or not shipping_info:
            return {'error': 'items and shipping_info are required'}, 400
        
        # Get pricing controller from app context
        from flask import current_app
        pricing_controller = current_app.extensions.get('pricing_controller')
        
        if not pricing_controller:
            return {'error': 'Pricing service not available'}, 500
        
        result = pricing_controller.get_shipping_estimates(items, shipping_info)
        
        if result['success']:
            return result['data']['shipping_options']
        else:
            return {'error': result['error']}, 400
