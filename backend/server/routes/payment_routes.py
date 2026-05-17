"""
Payment Routes for Go Postal SD Application

This module defines all payment-related API endpoints using Flask-RESTX.
It provides endpoints for processing payments, retrieving payment details, and handling refunds.
"""

from flask import request
from flask_restx import Namespace, Resource, fields
from server.services.payment_service import PaymentService
from server.middleware.auth_middleware import require_auth, require_role

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
    @api.marshal_with(payment_response_model)
    @require_auth
    def post(self):
        """Process a payment."""
        data = request.get_json()
        
        if not data:
            return {'error': 'Request body is required'}, 400
        
        # Validate required fields
        required_fields = ['amount', 'source_id']
        for field in required_fields:
            if field not in data:
                return {'error': f'{field} is required'}, 400
        
        # Validate amount
        if not isinstance(data['amount'], int) or data['amount'] <= 0:
            return {'error': 'Amount must be a positive integer'}, 400
        
        # Initialize payment service
        payment_service = PaymentService()
        
        if not payment_service.is_configured:
            return {'error': 'Payment service not configured'}, 500
        
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
            return {'error': result['error']}, 400

@api.route('/<string:payment_id>')
class PaymentResource(Resource):
    """Resource for retrieving payment details."""
    
    @api.doc('get_payment')
    @api.marshal_with(payment_response_model)
    @require_auth
    def get(self, payment_id):
        """Get payment details by ID."""
        if not payment_id:
            return {'error': 'Payment ID is required'}, 400
        
        # Initialize payment service
        payment_service = PaymentService()
        
        if not payment_service.is_configured:
            return {'error': 'Payment service not configured'}, 500
        
        # Get payment details
        result = payment_service.get_payment(payment_id)
        
        if result['success']:
            return result, 200
        else:
            return {'error': result['error']}, 404

@api.route('/refund')
class RefundResource(Resource):
    """Resource for processing refunds."""
    
    @api.doc('refund_payment')
    @api.expect(refund_request_model)
    @api.marshal_with(refund_response_model)
    @require_role('Admin')  # Only admins can process refunds
    def post(self):
        """Process a refund."""
        data = request.get_json()
        
        if not data:
            return {'error': 'Request body is required'}, 400
        
        # Validate required fields
        required_fields = ['payment_id', 'amount']
        for field in required_fields:
            if field not in data:
                return {'error': f'{field} is required'}, 400
        
        # Validate amount
        if not isinstance(data['amount'], int) or data['amount'] <= 0:
            return {'error': 'Amount must be a positive integer'}, 400
        
        # Initialize payment service
        payment_service = PaymentService()
        
        if not payment_service.is_configured:
            return {'error': 'Payment service not configured'}, 500
        
        # Process refund
        result = payment_service.refund_payment(
            payment_id=data['payment_id'],
            amount=data['amount'],
            reason=data.get('reason')
        )
        
        if result['success']:
            return result, 201
        else:
            return {'error': result['error']}, 400

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
                return {'error': 'Payment service not configured'}, 500
            
            # Validate webhook signature
            if not payment_service.validate_webhook(payload, signature, webhook_url):
                return {'error': 'Invalid webhook signature'}, 401
            
            # Process webhook (implement based on Square webhook events)
            # For now, just log the webhook
            logger.info(f"Received payment webhook: {payload}")
            
            return {'status': 'success'}, 200
            
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            return {'error': 'Internal server error'}, 500

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
