"""
Payment Routes for Go Postal SD Application

This module defines all payment-related API endpoints using Flask-RESTX.
It provides endpoints for processing payments, retrieving payment details, and handling refunds.
"""

from flask import request
from flask_restx import Namespace, Resource, fields
from server.services.payment_service import PaymentService
from server.middleware.auth_middleware import require_auth, require_role
from server.middleware.rate_limit_middleware import rate_limit_by_ip
from server.routes.response_utils import error_response
from server.config import database as db
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
    'payment_id': fields.String(description='Square payment ID (auto-resolved from order_id if omitted)'),
    'amount': fields.Integer(required=True, description='Refund amount in cents'),
    'reason': fields.String(description='Refund reason'),
    'order_id': fields.Integer(description='Internal order ID (used to resolve payment_id and update order status)')
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

def _handle_square_webhook_event(event_type: str, obj: dict) -> None:
    """Update our DB in response to Square-originated payment/refund events."""
    from server.models.order import Order, Payment as PaymentModel, Refund, PaymentStatus, OrderStatus
    from datetime import datetime

    if event_type in ('payment.updated', 'payment.created'):
        payment_data = obj.get('payment', {})
        square_payment_id = payment_data.get('id')
        square_status = payment_data.get('status', '')
        if not square_payment_id:
            return
        payment_row = PaymentModel.query.filter_by(external_payment_id=square_payment_id).first()
        if not payment_row:
            return
        if square_status == 'COMPLETED':
            payment_row.status = PaymentStatus.COMPLETED
            payment_row.order.payment_status = PaymentStatus.COMPLETED
        elif square_status in ('CANCELED', 'FAILED'):
            payment_row.status = PaymentStatus.FAILED
        db.session.commit()

    elif event_type in ('refund.updated', 'refund.created'):
        refund_data = obj.get('refund', {})
        square_payment_id = refund_data.get('payment_id')
        square_refund_id = refund_data.get('id')
        refund_status = refund_data.get('status', '')
        if not square_payment_id or refund_status != 'COMPLETED':
            return
        payment_row = PaymentModel.query.filter_by(external_payment_id=square_payment_id).first()
        if not payment_row:
            return
        order = payment_row.order
        # Only write DB refund record if we don't have one yet for this Square refund.
        existing = Refund.query.filter_by(external_refund_id=square_refund_id).first()
        if not existing:
            amount_money = refund_data.get('amount_money', {})
            refund_record = Refund(
                order_id=order.id,
                payment_id=payment_row.id,
                refund_amount=(amount_money.get('amount', 0)) / 100.0,
                currency=amount_money.get('currency', 'USD'),
                reason=refund_data.get('reason', 'Square-initiated refund'),
                external_refund_id=square_refund_id,
                provider_response=refund_data,
                processed_at=datetime.utcnow(),
            )
            db.session.add(refund_record)
        order.payment_status = PaymentStatus.REFUNDED
        order.status = OrderStatus.REFUNDED
        payment_row.status = PaymentStatus.REFUNDED
        db.session.commit()
        logger.info("Order %s marked refunded via Square webhook", order.id)


# Define resources
@api.route('/process')
class PaymentProcessResource(Resource):
    """Resource for processing payments."""
    
    @api.doc('process_payment')
    @api.expect(payment_request_model)
    @api.response(201, 'Payment processed', payment_response_model)
    @require_auth
    @rate_limit_by_ip('PAYMENT_RATE_LIMIT_COUNT', 'PAYMENT_RATE_LIMIT_WINDOW_SECONDS', 'payment-process')
    def post(self):
        """Process a payment."""
        data = request.get_json(silent=True)
        
        if not data:
            return error_response('Request body is required', 400)
        
        required_fields = ['source_id', 'order_id']
        for field in required_fields:
            if field not in data:
                return error_response(f'{field} is required', 400)

        # Validate amount against the actual order total — never trust the client amount.
        from server.models.order import Order as OrderModel, PaymentStatus as PS
        from flask import g
        internal_order_id = data.get('order_id')
        order_obj = OrderModel.query.get(internal_order_id) if internal_order_id else None
        if not order_obj:
            return error_response('Order not found', 404, code='ORDER_NOT_FOUND', category='business_logic')

        # Ownership check: non-admins may only pay for their own orders.
        current_user = getattr(g, 'current_user', None)
        if current_user and current_user.role.name != 'Admin':
            if order_obj.user_id is None or order_obj.user_id != current_user.id:
                return error_response('Access denied', 403, code='ACCESS_DENIED', category='authorization')

        if order_obj.payment_status == PS.COMPLETED:
            return error_response('Order already paid', 400, code='ORDER_ALREADY_PAID', category='business_logic')

        # Compute authoritative amount from DB — ignore any client-supplied amount.
        import math
        authoritative_amount = math.ceil(float(order_obj.total_amount) * 100)

        # Initialize payment service
        payment_service = PaymentService()

        if not payment_service.is_configured:
            return error_response('Payment service not configured', 500, code='PAYMENT_SERVICE_UNAVAILABLE', category='external_api', retryable=True)

        # Process payment
        result = payment_service.process_payment(
            amount=authoritative_amount,
            currency=order_obj.currency,
            source_id=data['source_id'],
            idempotency_key=data.get('idempotency_key'),
            buyer_email=order_obj.customer_email,
            buyer_phone=order_obj.customer_phone,
            shipping_address=order_obj.shipping_address,
            billing_address=order_obj.billing_address,
            note=f"Order {order_obj.order_number} payment"
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
    @require_role('Admin')
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
        
        if 'amount' not in data:
            return error_response('amount is required', 400)

        if not isinstance(data['amount'], int) or data['amount'] <= 0:
            return error_response('Amount must be a positive integer', 400)

        order_id = data.get('order_id')

        # Resolve the Square payment ID and validate the refund against the order.
        from server.models.order import Order as OrderModel, Payment as PaymentModel, PaymentStatus as PS, OrderStatus as OS
        import math

        order_obj = OrderModel.query.get(order_id) if order_id else None
        if order_id and not order_obj:
            return error_response('Order not found', 404, code='ORDER_NOT_FOUND', category='business_logic')

        if order_obj:
            if order_obj.payment_status == PS.REFUNDED:
                return error_response('Order has already been refunded', 400, code='ALREADY_REFUNDED', category='business_logic')
            # Refund amount must not exceed the original charge.
            max_refund_cents = math.ceil(float(order_obj.total_amount) * 100)
            if data['amount'] > max_refund_cents:
                return error_response(
                    f'Refund amount exceeds original charge ({max_refund_cents} cents)',
                    400, code='REFUND_EXCEEDS_CHARGE', category='business_logic'
                )

        # Resolve Square payment ID. Priority:
        #   1. Explicit payment_id in request body (manual override)
        #   2. Order.payment_id column (denormalised on checkout)
        #   3. Payment table row for the order
        square_payment_id = data.get('payment_id')

        if not square_payment_id and order_obj:
            if order_obj.payment_id:
                square_payment_id = order_obj.payment_id
            else:
                payment_row = PaymentModel.query.filter_by(order_id=order_id).order_by(
                    PaymentModel.created_at.desc()
                ).first()
                if payment_row:
                    square_payment_id = payment_row.external_payment_id

        if not square_payment_id:
            return error_response(
                'No payment record found for this order. If the payment was processed outside the system, enter the Square payment ID manually.',
                422, code='PAYMENT_ID_NOT_FOUND', category='business_logic'
            )

        # Initialize payment service
        payment_service = PaymentService()

        if not payment_service.is_configured:
            return error_response('Payment service not configured', 500, code='PAYMENT_SERVICE_UNAVAILABLE', category='external_api', retryable=True)

        # Process refund with Square
        result = payment_service.refund_payment(
            payment_id=square_payment_id,
            amount=data['amount'],
            reason=data.get('reason')
        )

        if result['success']:
            # Persist audit record and update order status in our DB.
            order_id = data.get('order_id')
            if order_id:
                try:
                    from server.models.order import Order, Payment as PaymentModel, Refund, PaymentStatus, OrderStatus
                    from datetime import datetime

                    order = Order.query.get(order_id)
                    if order:
                        # Look up our internal Payment row by Square payment ID.
                        payment_row = PaymentModel.query.filter_by(
                            order_id=order_id,
                            external_payment_id=square_payment_id
                        ).first()

                        refund_record = Refund(
                            order_id=order_id,
                            payment_id=payment_row.id if payment_row else None,
                            refund_amount=data['amount'] / 100.0,
                            currency='USD',
                            reason=data.get('reason') or 'Customer requested refund',
                            external_refund_id=result.get('refund_id'),
                            provider_response=result,
                            processed_at=datetime.utcnow(),
                        )
                        db.session.add(refund_record)

                        order.payment_status = PaymentStatus.REFUNDED
                        order.status = OrderStatus.REFUNDED
                        if payment_row:
                            payment_row.status = PaymentStatus.REFUNDED

                        db.session.commit()
                        logger.info("Refund record created and order %s marked refunded", order_id)
                except Exception:
                    logger.error("Error persisting refund record for order %s", order_id, exc_info=True)
                    db.session.rollback()
                    # Refund succeeded at Square; don't surface DB error to caller.

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
            signature = request.headers.get('X-Square-Signature', '').strip()
            # Build the canonical webhook URL from a configured base URL rather than
            # request.url, which is attacker-controlled via the Host header on a
            # misconfigured reverse proxy and would let an attacker forge HMAC messages.
            import os as _os
            _base = _os.getenv('SQUARE_WEBHOOK_URL') or _os.getenv('RENDER_EXTERNAL_URL')
            if not _base:
                logger.error("Webhook base URL not configured — set SQUARE_WEBHOOK_URL or RENDER_EXTERNAL_URL")
                return error_response('Webhook not configured', 500, code='WEBHOOK_CONFIG_ERROR', category='configuration')
            webhook_url = _base.rstrip('/') + '/api/payments/webhook'
            
            # Initialize payment service
            payment_service = PaymentService()
            
            if not payment_service.is_configured:
                return error_response('Payment service not configured', 500, code='PAYMENT_SERVICE_UNAVAILABLE', category='external_api', retryable=True)
            
            # Validate webhook signature
            if not payment_service.validate_webhook(payload, signature, webhook_url):
                return error_response('Invalid webhook signature', 401, code='INVALID_WEBHOOK_SIGNATURE', category='security')
            
            import json as _json
            try:
                event = _json.loads(payload)
            except Exception:
                event = {}

            event_type = event.get('type', '')
            logger.info("Received Square webhook: %s", event_type)

            try:
                _handle_square_webhook_event(event_type, event.get('data', {}).get('object', {}))
            except Exception:
                logger.error("Error handling webhook event %s", event_type, exc_info=True)

            return {'status': 'success'}, 200
            
        except Exception:
            logger.error("Error processing webhook", exc_info=True)
            return error_response('Internal server error', 500, category='system', retryable=True)

@api.route('/status')
class PaymentStatusResource(Resource):
    """Resource for checking payment service status."""

    @api.doc('get_payment_status')
    @require_role('Admin')
    def get(self):
        """Get payment service status and configuration."""
        payment_service = PaymentService()
        
        return {
            'configured': payment_service.is_configured,
            'provider_info': payment_service.get_provider_info()
        }, 200
