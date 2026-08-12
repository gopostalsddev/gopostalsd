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
from server.square_config import SquareConfigurationError, square_webhook_url
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
    from server.models.order import (
        Payment as PaymentModel, PaymentAttempt, Refund, RefundAttempt,
        PaymentStatus, OrderStatus,
    )
    from datetime import datetime

    if event_type in ('payment.updated', 'payment.created'):
        payment_data = obj.get('payment', {})
        square_payment_id = payment_data.get('id')
        square_status = payment_data.get('status', '')
        if not square_payment_id:
            return
        payment_row = PaymentModel.query.filter_by(
            payment_provider='square', external_payment_id=square_payment_id
        ).first()
        attempt = None
        if not payment_row and payment_data.get('reference_id'):
            attempt = PaymentAttempt.query.filter_by(
                provider='square',
                provider_reference=payment_data['reference_id'],
            ).first()
            if attempt:
                amount_money = payment_data.get('amount_money', {})
                if (
                    amount_money.get('amount') != attempt.amount_cents
                    or amount_money.get('currency') != attempt.currency
                ):
                    raise ValueError('Square webhook amount does not match payment attempt')
        if square_status == 'COMPLETED':
            order = payment_row.order if payment_row else (attempt.order if attempt else None)
            if not payment_row and attempt:
                payment_row = PaymentModel(
                    order_id=attempt.order_id,
                    payment_provider='square',
                    external_payment_id=square_payment_id,
                    amount=attempt.amount_cents / 100,
                    currency=attempt.currency,
                    status=PaymentStatus.COMPLETED,
                    payment_method='card',
                    provider_response=payment_data,
                )
                db.session.add(payment_row)
            if not payment_row:
                return
            payment_row.status = PaymentStatus.COMPLETED
            order.payment_status = PaymentStatus.COMPLETED
            order.status = OrderStatus.PROCESSING
            order.payment_provider = 'square'
            order.payment_id = square_payment_id
            if attempt:
                attempt.status = 'succeeded'
                attempt.external_payment_id = square_payment_id
                attempt.provider_response = payment_data
                attempt.completed_at = datetime.utcnow()
        elif square_status in ('CANCELED', 'FAILED'):
            if payment_row:
                payment_row.status = PaymentStatus.FAILED
            if attempt:
                attempt.status = 'failed'
                attempt.last_error_code = 'provider_declined'
                attempt.order.payment_status = PaymentStatus.PENDING

    elif event_type in ('refund.updated', 'refund.created'):
        refund_data = obj.get('refund', {})
        square_payment_id = refund_data.get('payment_id')
        square_refund_id = refund_data.get('id')
        refund_status = refund_data.get('status', '')
        if not square_payment_id or not square_refund_id:
            return
        payment_row = PaymentModel.query.filter_by(
            payment_provider='square', external_payment_id=square_payment_id
        ).first()
        if not payment_row:
            return
        order = payment_row.order
        existing = Refund.query.filter_by(external_refund_id=square_refund_id).first()
        amount_money = refund_data.get('amount_money', {})
        amount_cents = amount_money.get('amount')
        currency = amount_money.get('currency', payment_row.currency)
        attempt = RefundAttempt.query.filter_by(
            external_refund_id=square_refund_id
        ).first()
        if not attempt and amount_cents is not None:
            attempt = (
                RefundAttempt.query.filter(
                    RefundAttempt.payment_id == payment_row.id,
                    RefundAttempt.amount_cents == amount_cents,
                    RefundAttempt.currency == currency,
                    RefundAttempt.status.in_(('reserved', 'processing', 'unknown')),
                )
                .order_by(RefundAttempt.id.desc())
                .first()
            )

        if refund_status == 'COMPLETED':
            if attempt and (
                attempt.amount_cents != amount_cents or attempt.currency != currency
            ):
                raise ValueError('Square webhook amount does not match refund attempt')
            if not existing:
                existing = Refund(
                    order_id=order.id,
                    payment_id=payment_row.id,
                    refund_amount=(amount_cents or 0) / 100.0,
                    currency=currency,
                    reason=refund_data.get('reason', 'Square-initiated refund'),
                    external_refund_id=square_refund_id,
                    provider_response=refund_data,
                    processed_at=datetime.utcnow(),
                )
                db.session.add(existing)
                db.session.flush()
            if attempt:
                attempt.status = 'succeeded'
                attempt.external_refund_id = square_refund_id
                attempt.provider_response = refund_data
                attempt.completed_at = datetime.utcnow()
            from sqlalchemy import func as _func
            from decimal import Decimal
            refunded = db.session.query(
                _func.coalesce(_func.sum(Refund.refund_amount), 0)
            ).filter_by(payment_id=payment_row.id).scalar()
            fully_refunded = Decimal(str(refunded)) >= Decimal(str(payment_row.amount))
            payment_row.status = (
                PaymentStatus.REFUNDED if fully_refunded
                else PaymentStatus.PARTIALLY_REFUNDED
            )
            order.payment_status = payment_row.status
            if fully_refunded:
                order.status = OrderStatus.REFUNDED
            logger.info("Order %s refund reconciled via Square webhook", order.id)
        elif refund_status in ('FAILED', 'REJECTED', 'CANCELED') and attempt:
            attempt.status = 'failed'
            attempt.last_error_code = 'provider_rejected'


# Define resources
@api.route('/process')
class PaymentProcessResource(Resource):
    """Retired bypass route; charging belongs to the order lifecycle."""
    
    @api.doc('process_payment')
    @api.response(410, 'Use the canonical order payment endpoint')
    @require_auth
    @rate_limit_by_ip('PAYMENT_RATE_LIMIT_COUNT', 'PAYMENT_RATE_LIMIT_WINDOW_SECONDS', 'payment-process')
    def post(self):
        """Process a payment."""
        return error_response(
            'This payment endpoint is retired; use /api/orders/<order_id>/payment',
            410,
            code='PAYMENT_ROUTE_RETIRED',
            category='business_logic',
        )

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
        if not order_id:
            return error_response('order_id is required', 400, code='ORDER_ID_REQUIRED', category='business_logic')

        from server.services.refund_service import RefundService

        payment_service = PaymentService()
        if not payment_service.is_configured:
            return error_response(
                'Payment service not configured', 500,
                code='PAYMENT_SERVICE_UNAVAILABLE', category='external_api',
                retryable=True,
            )

        result = RefundService(payment_service).process_refund(
            order_id=order_id,
            amount_cents=data['amount'],
            reason=data.get('reason'),
            external_payment_id=data.get('payment_id'),
        )
        if result['success']:
            return result, 201
        code = result.get('code', 'PAYMENT_REFUND_ERROR')
        status = {
            'ORDER_NOT_FOUND': 404,
            'PAYMENT_ID_NOT_FOUND': 422,
            'REFUND_EXCEEDS_CHARGE': 400,
            'REFUND_OUTCOME_UNKNOWN': 503,
            'REFUND_RECONCILIATION_FAILED': 503,
        }.get(code, 409)
        return error_response(
            result['error'], status,
            code=code,
            category='business_logic',
            retryable=code in {
                'REFUND_OUTCOME_UNKNOWN', 'REFUND_RECONCILIATION_FAILED'
            },
        )

@api.route('/webhook')
class WebhookResource(Resource):
    """Resource for handling payment webhooks."""
    
    @api.doc('handle_webhook')
    def post(self):
        """Handle payment webhook notifications."""
        try:
            # Get webhook data
            payload = request.get_data(cache=True)
            signature = request.headers.get(
                'x-square-hmacsha256-signature', ''
            ).strip()
            # Square signs the exact configured notification URL. Never derive it
            # from request host/proxy headers or append a path to a base URL.
            try:
                webhook_url = square_webhook_url()
            except SquareConfigurationError:
                logger.error("Square webhook URL is not configured correctly")
                return error_response('Webhook not configured', 500, code='WEBHOOK_CONFIG_ERROR', category='configuration')
            
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
                return error_response('Invalid webhook payload', 400, code='INVALID_WEBHOOK_PAYLOAD', category='validation')

            if not isinstance(event, dict):
                return error_response('Invalid webhook payload', 400, code='INVALID_WEBHOOK_PAYLOAD', category='validation')

            event_type = event.get('type', '')
            event_id = event.get('event_id', '')
            if not isinstance(event_id, str) or not event_id.strip() or not isinstance(event_type, str) or not event_type.strip():
                return error_response('Webhook event_id and type are required', 400, code='INVALID_WEBHOOK_EVENT', category='validation')
            logger.info("Received Square webhook: %s", event_type)

            from server.services.square_webhook_inbox import (
                WebhookEventConflict, claim_event, mark_failed,
                mark_processed, register_event,
            )
            try:
                receipt, _created = register_event(
                    event_id.strip(), event_type.strip(), event, payload
                )
            except WebhookEventConflict:
                logger.error("Square event ID was reused with different content")
                return error_response('Webhook event conflict', 409, code='WEBHOOK_EVENT_CONFLICT', category='security')

            if not claim_event(receipt.id):
                return {'status': 'duplicate'}, 200

            try:
                _handle_square_webhook_event(event_type, event.get('data', {}).get('object', {}))
                mark_processed(receipt.id)
            except Exception as exc:
                logger.error("Error handling webhook event %s", event_type, exc_info=True)
                mark_failed(receipt.id, exc)
                return error_response('Webhook processing failed', 503, code='WEBHOOK_PROCESSING_FAILED', category='system', retryable=True)

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
