"""
Order Routes for Go Postal SD Application

This module defines all order-related API endpoints using Flask-RESTX.
It provides order creation, payment processing, and order management functionality.
"""

from flask import request, g
from flask_restx import Namespace, Resource, fields
from server.services.order_service import OrderService
from server.services.payment_service import PaymentService
from server.services.email_service import EmailService
from server.middleware.auth_middleware import require_auth, require_role, optional_auth, get_user_id
from server.factories.main_factory import MainFactory
from server.validation.input_validator import (
    validate_address_input,
    validate_email_input,
    validate_string_input,
    validator,
)
from server.routes.response_utils import error_response

# Create namespace for order operations
api = Namespace('orders', description='Order operations')

# Define models for API documentation
order_item_model = api.model('OrderItem', {
    'id': fields.Integer(description='Order item ID'),
    'product_id': fields.Integer(description='Product ID'),
    'product_name': fields.String(description='Product name'),
    'product_sku': fields.String(description='Product SKU'),
    'quantity': fields.Integer(description='Quantity'),
    'unit_price': fields.Float(description='Unit price'),
    'total_price': fields.Float(description='Total price'),
    'selected_options': fields.Raw(description='Selected options'),
    'package_info': fields.Raw(description='Package information')
})

order_model = api.model('Order', {
    'id': fields.Integer(description='Order ID'),
    'order_number': fields.String(description='Order number'),
    'user_id': fields.Integer(description='User ID'),
    'session_id': fields.String(description='Session ID'),
    'customer_email': fields.String(description='Customer email'),
    'customer_first_name': fields.String(description='Customer first name'),
    'customer_last_name': fields.String(description='Customer last name'),
    'customer_phone': fields.String(description='Customer phone'),
    'status': fields.String(description='Order status'),
    'subtotal': fields.Float(description='Subtotal'),
    'shipping_cost': fields.Float(description='Shipping cost'),
    'tax_amount': fields.Float(description='Tax amount'),
    'total_amount': fields.Float(description='Total amount'),
    'currency': fields.String(description='Currency'),
    'shipping_address': fields.Raw(description='Shipping address'),
    'billing_address': fields.Raw(description='Billing address'),
    'payment_status': fields.String(description='Payment status'),
    'payment_provider': fields.String(description='Payment provider'),
    'payment_id': fields.String(description='Payment ID'),
    'tracking_number': fields.String(description='Tracking number'),
    'carrier_name': fields.String(description='Carrier name'),
    'estimated_delivery': fields.String(description='Estimated delivery date'),
    'shipped_at': fields.String(description='Shipped timestamp'),
    'delivered_at': fields.String(description='Delivered timestamp'),
    'items': fields.List(fields.Nested(order_item_model), description='Order items'),
    'created_at': fields.String(description='Created timestamp'),
    'updated_at': fields.String(description='Updated timestamp')
})

create_order_model = api.model('CreateOrderRequest', {
    'customer_info': fields.Nested(api.model('CustomerInfo', {
        'email': fields.String(description='Customer email', required=True),
        'first_name': fields.String(description='Customer first name', required=True),
        'last_name': fields.String(description='Customer last name', required=True),
        'phone': fields.String(description='Customer phone')
    }), required=True),
    'shipping_address': fields.Nested(api.model('Address', {
        'street': fields.String(description='Street address', required=True),
        'city': fields.String(description='City', required=True),
        'state': fields.String(description='State/Province', required=True),
        'zip_code': fields.String(description='ZIP/Postal code', required=True),
        'country': fields.String(description='Country', required=True),
        'apt': fields.String(description='Apartment/Suite number')
    }), required=True),
    'billing_address': fields.Nested(api.model('BillingAddress', {
        'street': fields.String(description='Street address', required=True),
        'city': fields.String(description='City', required=True),
        'state': fields.String(description='State/Province', required=True),
        'zip_code': fields.String(description='ZIP/Postal code', required=True),
        'country': fields.String(description='Country', required=True),
        'apt': fields.String(description='Apartment/Suite number')
    }), description='Billing address (optional)')
})

payment_model = api.model('PaymentRequest', {
    'source_id': fields.String(description='Payment source ID (card nonce)', required=True),
    'payment_method': fields.String(description='Payment method', default='card')
})

update_status_model = api.model('UpdateStatusRequest', {
    'status': fields.String(description='New order status', required=True),
    'tracking_number': fields.String(description='Tracking number'),
    'carrier_name': fields.String(description='Carrier name')
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

def get_order_service():
    """Get order service instance."""
    payment_service = PaymentService()
    email_service = main_factory.get_email_service()
    return OrderService(payment_service, email_service)

# Define resources
@api.route('/')
class OrderResource(Resource):
    """Resource for order operations."""

    @api.doc('get_all_orders')
    @api.response(200, 'Orders list retrieved')
    @require_role('Admin')
    def get(self):
        """Get all orders for admin management."""
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        status = request.args.get('status')

        order_service = get_order_service()
        result = order_service.get_all_orders(limit=limit, offset=offset, status=status)

        if result['success']:
            return {
                'orders': result['orders'],
                'total_count': result['total_count'],
                'limit': result['limit'],
                'offset': result['offset']
            }, 200
        else:
            return error_response(result['error'], 400, code='ORDER_LIST_ERROR', category='business_logic')
    
    @api.doc('create_order')
    @api.expect(create_order_model)
    @api.response(201, 'Order created', order_model)
    @optional_auth
    def post(self):
        """Create order from cart."""
        data = request.get_json(silent=True)
        
        if not data:
            return error_response('Request body is required', 400)
        
        # Validate required fields
        if 'customer_info' not in data or 'shipping_address' not in data:
            return error_response('customer_info and shipping_address are required', 400)
        
        customer_info = data['customer_info']
        required_customer_fields = ['email', 'first_name', 'last_name']
        for field in required_customer_fields:
            if field not in customer_info:
                return error_response(f'customer_info.{field} is required', 400)

        email_result = validate_email_input(customer_info.get('email'))
        if not email_result.is_valid:
            return error_response('Invalid customer email', 400)

        first_name_result = validate_string_input(customer_info.get('first_name'), max_length=100)
        last_name_result = validate_string_input(customer_info.get('last_name'), max_length=100)
        if not first_name_result.is_valid or not last_name_result.is_valid:
            return error_response('Invalid customer name', 400)

        phone_value = customer_info.get('phone')
        sanitized_phone = None
        if phone_value:
            phone_result = validator.validate_phone(phone_value)
            if not phone_result.is_valid:
                return error_response('Invalid customer phone', 400)
            sanitized_phone = phone_result.sanitized_data
        
        shipping_address = data['shipping_address']
        shipping_address_result = validate_address_input(shipping_address)
        if not shipping_address_result.is_valid:
            return error_response('Invalid shipping_address', 400)

        billing_address = data.get('billing_address')
        sanitized_billing_address = None
        if billing_address:
            billing_address_result = validate_address_input(billing_address)
            if not billing_address_result.is_valid:
                return error_response('Invalid billing_address', 400)
            sanitized_billing_address = billing_address_result.sanitized_data
        
        session_id, session_error = _get_required_session_id()
        if session_error:
            return session_error
        user_id = get_user_id()
        
        order_service = get_order_service()
        result = order_service.create_order_from_cart(
            session_id=session_id,
            customer_info={
                'email': email_result.sanitized_data,
                'first_name': first_name_result.sanitized_data,
                'last_name': last_name_result.sanitized_data,
                'phone': sanitized_phone,
            },
            shipping_address=shipping_address_result.sanitized_data,
            billing_address=sanitized_billing_address,
            user_id=user_id
        )
        
        if result['success']:
            return result['order'], 201
        else:
            return error_response(result['error'], 400, code='ORDER_CREATE_ERROR', category='business_logic')

@api.route('/<int:order_id>')
class OrderDetailResource(Resource):
    """Resource for order details."""
    
    @api.doc('get_order')
    @api.response(200, 'Order retrieved', order_model)
    @require_auth
    def get(self, order_id):
        """Get order details."""
        # Get user_id from auth context
        user_id = getattr(request, 'user_id', None)
        
        order_service = get_order_service()
        result = order_service.get_order(order_id, user_id)
        
        if result['success']:
            return result['order'], 200
        else:
            return error_response(result['error'], 404, code='ORDER_NOT_FOUND', category='business_logic')

@api.route('/<int:order_id>/payment')
class PaymentResource(Resource):
    """Resource for processing payments."""
    
    @api.doc('process_payment')
    @api.expect(payment_model)
    @api.response(200, 'Payment processed for order')
    @require_auth
    def post(self, order_id):
        """Process payment for order."""
        data = request.get_json()
        
        if not data or 'source_id' not in data:
            return error_response('source_id is required', 400)
        
        order_service = get_order_service()

        # Non-admin users can only process payment for their own orders.
        current_user = getattr(g, 'current_user', None)
        request_user_id = getattr(request, 'user_id', None)
        if not current_user:
            return error_response('Authentication required', 401, code='AUTH_REQUIRED', category='authentication')

        if current_user.role.name != 'Admin':
            ownership_result = order_service.get_order(order_id, request_user_id)
            if not ownership_result['success']:
                if ownership_result['error'] == 'Order not found':
                    return error_response('Order not found', 404, code='ORDER_NOT_FOUND', category='business_logic')
                return error_response('Access denied', 403, code='ACCESS_DENIED', category='authorization')

        result = order_service.process_payment(order_id, data)
        
        if result['success']:
            return {
                'success': True,
                'payment': result['payment'],
                'order': result['order']
            }, 200
        else:
            return error_response(result['error'], 400, code='ORDER_PAYMENT_ERROR', category='business_logic')

@api.route('/user/<int:user_id>')
class UserOrdersResource(Resource):
    """Resource for user orders."""
    
    @api.doc('get_user_orders')
    @api.response(200, 'User orders retrieved')
    @require_auth
    def get(self, user_id):
        """Get user's orders."""
        # Verify user can only access their own orders
        request_user_id = getattr(request, 'user_id', None)
        if request_user_id != user_id:
            return error_response('Access denied', 403, code='ACCESS_DENIED', category='authorization')
        
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        order_service = get_order_service()
        result = order_service.get_user_orders(user_id, limit, offset)
        
        if result['success']:
            return {
                'orders': result['orders'],
                'total_count': result['total_count'],
                'limit': result['limit'],
                'offset': result['offset']
            }, 200
        else:
            return error_response(result['error'], 400, code='USER_ORDER_LIST_ERROR', category='business_logic')

@api.route('/<int:order_id>/status')
class OrderStatusResource(Resource):
    """Resource for updating order status (admin only)."""
    
    @api.doc('update_order_status')
    @api.expect(update_status_model)
    @api.response(200, 'Order status updated', order_model)
    @require_role('Admin')
    def put(self, order_id):
        """Update order status."""
        data = request.get_json()
        
        if not data or 'status' not in data:
            return error_response('status is required', 400)
        
        from server.models.order import OrderStatus
        
        try:
            status = OrderStatus(data['status'])
        except ValueError:
            return error_response('Invalid status value', 400)
        
        order_service = get_order_service()
        result = order_service.update_order_status(
            order_id=order_id,
            status=status,
            tracking_number=data.get('tracking_number'),
            carrier_name=data.get('carrier_name')
        )
        
        if result['success']:
            return result['order'], 200
        else:
            return error_response(result['error'], 400, code='ORDER_STATUS_UPDATE_ERROR', category='business_logic')

@api.route('/statuses')
class OrderStatusesResource(Resource):
    """Resource for getting available order statuses."""
    
    @api.doc('get_order_statuses')
    @api.marshal_with(api.model('OrderStatuses', {
        'statuses': fields.List(fields.String, description='Available order statuses')
    }))
    def get(self):
        """Get available order statuses."""
        from server.models.order import OrderStatus
        
        return {
            'statuses': [status.value for status in OrderStatus]
        }, 200
