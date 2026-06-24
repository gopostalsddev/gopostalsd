"""
Payment Routes for Go Postal SD Application

This module defines all payment-related API endpoints using Flask-RESTX.
It provides endpoints for processing payments, retrieving payment details, and handling refunds.
"""

from flask import request
from flask_restx import Namespace, Resource, fields
from server.services.payment_service import PaymentService
from server.middleware.auth_middleware import require_auth, require_role
from server.routes.response_utils import error_response
import logging

logger = logging.getLogger(__name__)

# Create namespace for payment operations
api = Namespace('payments', description='Payment processing operations')

# Define models for API documentation
payment_request_model = api.model('PaymentRequest', {
    'amount': fields.Integer(required=True, description='Payment amount in cents (e.g., 1000 = $10.00)'),
    'currency': fields.String(description='Currency code (default: USD)', default='USD'),
    'source_id': fields.String(required=True, description='Payment source ID (card nonce from Square Web Payments SDK)'),
    'idempotency_key': fields.String(description='Unique key to prevent duplicate payments'),
    'buyer_email': fields.String(description='Buyer email address'),
    'buyer_phone': fields.String(description='Buyer phone number'),
    'shipping_address': fields.Nested(api.model('Address', {
        'street': fields.String(required=True, description='Street address'),
        'city': fields.String(required=True, description='City'),
        'state': fields.String(required=True, description='State/Province'),
        'zip_code': fields.String(required=True, description='ZIP/Postal code'),
        'country': fields.String(required=True, description='Country'),
        'apt': fields.String(description='Apartment/Suite number')
    }), description='Shipping address'),
    'billing_address': fields.Nested(api.model('BillingAddress', {
        'street': fields.String(required=True, description='Street address'),
        'city': fields.String(required=True, description='City'),
        'state': fields.String(required=True, description='State/Province'),
        'zip_code': fields.String(required=True, description='ZIP/Postal code'),
        'country': fields.String(required=True, description='Country'),
        'apt': fields.String(description='Apartment/Suite number')
    }), description='Billing address'),
    'order_id': fields.String(description='Order identifier'),
    'note': fields.String(description='Payment note')
})

payment_response_model = api.model('PaymentResponse', {
    'success': fields.Boolean(description='Payment success status'),
    'payment_id': fields.String(description='Payment ID'),
    'status': fields.String(description='Payment status'),
    'amount': fields.Integer(description='Payment amount in cents'),
    'currency': fields.String(description='Currency code'),
    'created_at': fields.String(description='Payment creation timestamp'),
    'receipt_url': fields.String(description='Receipt URL'),
    'order_id': fields.String(description='Order ID'),
    'error': fields.String(description='Error message if payment failed')
})

refund_request_model = api.model('RefundRequest', {
    'payment_id': fields.String(required=True, description='Payment ID to refund'),
    'amount': fields.Integer(required=True, description='Refund amount in cents'),
    'reason': fields.String(description='Refund reason')
})

refund_response_model = api.model('RefundResponse', {
    'success': fields.Boolean(description='Refund success status'),
    'refund_id': fields.String(description='Refund ID'),
    'payment_id': fields.String(description='Original payment ID'),
    'amount': fields.Integer(description='Refund amount in cents'),
    'status': fields.String(description='Refund status'),
    'reason': fields.String(description='Refund reason'),
    'created_at': fields.String(description='Refund creation timestamp'),
    'error': fields.String(description='Error message if refund failed')
})

# Define resources
@api.route('/process')
class PaymentProcessResource(Resource):
    """Resource for processing payments."""
    
    @api.doc('process_payment')
    @api.expect(payment_request_model)
    @api.response(201, 'Payment processed', payment_response_model)
    @require_auth
    def post(self):
        """Process a payment."""
        data = request.get_json(silent=True)
        
        if not data:
            return error_response('Request body is required', 400)
        
        # Validate required fields
        required_fields = ['amount', 'source_id']
        for field in required_fields:
            if field not in data:
                return error_response(f'{field} is required', 400)
        
        # Validate amount
        if not isinstance(data['amount'], int) or data['amount'] <= 0:
            return error_response('Amount must be a positive integer', 400)
        
        # Initialize payment service
        payment_service = PaymentService()
        
        if not payment_service.is_configured:
            return error_response('Payment service not configured', 500, code='PAYMENT_SERVICE_UNAVAILABLE', category='external_api', retryable=True)
        
        # Process payment
        result = payment_service.process_payment(
            amount=data['amount'],
            currency=data.get('currency', 'USD'),
            source_id=data['source_id'],
            idempotency_key=data.get('idempotency_key'),
            buyer_email=data.get('buyer_email'),
            buyer_phone=data.get('buyer_phone'),
            shipping_address=data.get('shipping_address'),
            billing_address=data.get('billing_address'),
            order_id=data.get('order_id'),
            note=data.get('note')
        )
        
        if result['success']:
            return result, 201
        else:
            return error_response(result['error'], 400, code='PAYMENT_PROCESSING_ERROR', category='external_api')

@api.route('/<string:payment_id>')
class PaymentResource(Resource):
    """Resource for retrieving payment details."""
    
    @api.doc('get_payment')
    @api.response(200, 'Payment fetched', payment_response_model)
    @require_auth
    def get(self, payment_id):
        """Get payment details by ID."""
        if not payment_id:
            return error_response('Payment ID is required', 400)
        
        # Initialize payment service
        payment_service = PaymentService()
        
        if not payment_service.is_configured:
            return error_response('Payment service not configured', 500, code='PAYMENT_SERVICE_UNAVAILABLE', category='external_api', retryable=True)
        
        # Get payment details
        result = payment_service.get_payment(payment_id)
        
        if result['success']:
            return result, 200
        else:
            return error_response(result['error'], 404, code='PAYMENT_NOT_FOUND', category='business_logic')

@api.route('/refund')
class RefundResource(Resource):
    """Resource for processing refunds."""
    
    @api.doc('refund_payment')
    @api.expect(refund_request_model)
    @api.response(201, 'Refund processed', refund_response_model)
    @require_role('Admin')  # Only admins can process refunds
    def post(self):
        """Process a refund."""
        data = request.get_json(silent=True)
        
        if not data:
            return error_response('Request body is required', 400)
        
        # Validate required fields
        required_fields = ['payment_id', 'amount']
        for field in required_fields:
            if field not in data:
                return error_response(f'{field} is required', 400)
        
        # Validate amount
        if not isinstance(data['amount'], int) or data['amount'] <= 0:
            return error_response('Amount must be a positive integer', 400)
        
        # Initialize payment service
        payment_service = PaymentService()
        
        if not payment_service.is_configured:
            return error_response('Payment service not configured', 500, code='PAYMENT_SERVICE_UNAVAILABLE', category='external_api', retryable=True)
        
        # Process refund
        result = payment_service.refund_payment(
            payment_id=data['payment_id'],
            amount=data['amount'],
            reason=data.get('reason')
        )
        
        if result['success']:
            return result, 201
        else:
            return error_response(result['error'], 400, code='PAYMENT_REFUND_ERROR', category='external_api')

@api.route('/webhook')
class WebhookResource(Resource):
    """Resource for handling payment webhooks."""
    
    @api.doc('handle_webhook')
    def post(self):
        """Handle payment webhook notifications."""
        try:
            # Get webhook data
            payload = request.get_data(as_text=True)
            signature = request.headers.get('X-Square-Signature', '')
            webhook_url = request.url
            
            # Initialize payment service
            payment_service = PaymentService()
            
            if not payment_service.is_configured:
                return error_response('Payment service not configured', 500, code='PAYMENT_SERVICE_UNAVAILABLE', category='external_api', retryable=True)
            
            # Validate webhook signature
            if not payment_service.validate_webhook(payload, signature, webhook_url):
                return error_response('Invalid webhook signature', 401, code='INVALID_WEBHOOK_SIGNATURE', category='security')
            
            # Process webhook (implement based on Square webhook events)
            # For now, just log the webhook
            logger.info("Received payment webhook")
            
            return {'status': 'success'}, 200
            
        except Exception:
            logger.error("Error processing webhook", exc_info=True)
            return error_response('Internal server error', 500, category='system', retryable=True)

@api.route('/status')
class PaymentStatusResource(Resource):
    """Resource for checking payment service status."""
    
    @api.doc('get_payment_status')
    def get(self):
        """Get payment service status and configuration."""
        payment_service = PaymentService()
        
        return {
            'configured': payment_service.is_configured,
            'provider_info': payment_service.get_provider_info()
        }, 200
