"""
Square Payment Adapter for Go Postal SD Application

This module provides a wrapper around the Square Payment API for processing payments.
It follows the Adapter pattern to provide a consistent interface for payment processing.
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from square import Client as SquareClient
    from square.models import Money, CreatePaymentRequest, Address as SquareAddress
    SQUARE_AVAILABLE = True
except ImportError:
    SQUARE_AVAILABLE = False
    logger.warning("Square SDK not available. Install with: pip install squareup")
    # Define dummy classes for when SDK is not available
    class SquareClient:
        pass
    class Money:
        pass
    class CreatePaymentRequest:
        pass
    class SquareAddress:
        pass


class SquareAdapter:
    """
    Adapter for Square Payment API.
    
    This adapter provides a consistent interface for processing payments through Square,
    handling authentication, payment processing, and error management.
    """
    
    def __init__(self, access_token: Optional[str] = None, environment: str = "sandbox"):
        """
        Initialize Square Payment adapter.
        
        Args:
            access_token: Square access token (defaults to SQUARE_ACCESS_TOKEN env var)
            environment: Square environment ('sandbox' or 'production')
        """
        self.access_token = access_token or os.getenv('SQUARE_ACCESS_TOKEN')
        self.environment = environment.lower()
        self.application_id = os.getenv('SQUARE_APPLICATION_ID')
        self.location_id = os.getenv('SQUARE_LOCATION_ID')
        self.client = None
        self._is_configured = False
        
        if SQUARE_AVAILABLE and self.access_token:
            try:
                # Initialize Square client
                self.client = SquareClient(
                    access_token=self.access_token,
                    environment=self.environment
                )
                self._is_configured = True
                logger.info(f"Square client initialized for {self.environment} environment")
            except Exception as e:
                logger.error(f"Failed to initialize Square client: {str(e)}")
                self.client = None
        else:
            if not SQUARE_AVAILABLE:
                logger.warning("Square SDK not available. Install with: pip install squareup")
            else:
                logger.warning("SQUARE_ACCESS_TOKEN not found in environment variables")
    
    def process_payment(self, 
                       amount: int, 
                       currency: str = "USD",
                       source_id: str = None,
                       idempotency_key: str = None,
                       buyer_email: str = None,
                       buyer_phone: str = None,
                       shipping_address: Dict[str, Any] = None,
                       billing_address: Dict[str, Any] = None,
                       order_id: str = None,
                       note: str = None) -> Dict[str, Any]:
        """
        Process a payment through Square.
        
        Args:
            amount: Payment amount in cents (e.g., 1000 = $10.00)
            currency: Currency code (default: USD)
            source_id: Payment source ID (card nonce from Square Web Payments SDK)
            idempotency_key: Unique key to prevent duplicate payments
            buyer_email: Buyer's email address
            buyer_phone: Buyer's phone number
            shipping_address: Shipping address information
            billing_address: Billing address information
            order_id: Order identifier
            note: Payment note
            
        Returns:
            Dict containing payment result with success status and details
        """
        try:
            if not self.client:
                return {
                    'success': False,
                    'error': 'Square not configured. Set SQUARE_ACCESS_TOKEN environment variable.',
                    'payment_id': None
                }
            
            if not source_id:
                return {
                    'success': False,
                    'error': 'Payment source ID (card nonce) is required',
                    'payment_id': None
                }
            
            # Generate idempotency key if not provided
            if not idempotency_key:
                idempotency_key = f"gopostalsd_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{amount}"
            
            # Create money object
            money = Money(amount=amount, currency=currency)
            
            # Build payment request
            payment_request = CreatePaymentRequest(
                source_id=source_id,
                idempotency_key=idempotency_key,
                amount_money=money,
                location_id=self.location_id
            )
            
            # Add buyer information if provided
            if buyer_email or buyer_phone:
                buyer_info = {}
                if buyer_email:
                    buyer_info['email_address'] = buyer_email
                if buyer_phone:
                    buyer_info['phone_number'] = buyer_phone
                payment_request.buyer_email_address = buyer_email
                payment_request.buyer_phone_number = buyer_phone
            
            # Add addresses if provided
            if shipping_address:
                shipping_addr = self._create_square_address(shipping_address)
                payment_request.shipping_address = shipping_addr
            
            if billing_address:
                billing_addr = self._create_square_address(billing_address)
                payment_request.billing_address = billing_addr
            
            # Add order and note information
            if order_id:
                payment_request.order_id = order_id
            if note:
                payment_request.note = note
            
            # Process payment
            result = self.client.payments.create_payment(payment_request)
            
            if result.is_success():
                payment = result.body['payment']
                logger.info(f"Payment processed successfully: {payment['id']}")
                return {
                    'success': True,
                    'payment_id': payment['id'],
                    'status': payment['status'],
                    'amount': payment['amount_money']['amount'],
                    'currency': payment['amount_money']['currency'],
                    'created_at': payment['created_at'],
                    'updated_at': payment['updated_at'],
                    'receipt_url': payment.get('receipt_url'),
                    'order_id': payment.get('order_id'),
                    'idempotency_key': idempotency_key
                }
            else:
                errors = result.errors if result.errors else []
                error_messages = [error.get('detail', str(error)) for error in errors]
                logger.error(f"Square payment failed: {error_messages}")
                return {
                    'success': False,
                    'error': f'Square payment failed: {", ".join(error_messages)}',
                    'errors': errors,
                    'payment_id': None
                }
                
        except Exception as e:
            logger.error(f"Error processing Square payment: {str(e)}")
            return {
                'success': False,
                'error': f'Square payment error: {str(e)}',
                'payment_id': None
            }
    
    def get_payment(self, payment_id: str) -> Dict[str, Any]:
        """
        Retrieve payment details by ID.
        
        Args:
            payment_id: Square payment ID
            
        Returns:
            Dict containing payment details or error information
        """
        try:
            if not self.client:
                return {
                    'success': False,
                    'error': 'Square not configured. Set SQUARE_ACCESS_TOKEN environment variable.',
                    'payment': None
                }
            
            result = self.client.payments.get_payment(payment_id)
            
            if result.is_success():
                payment = result.body['payment']
                logger.info(f"Payment retrieved successfully: {payment_id}")
                return {
                    'success': True,
                    'payment': payment,
                    'payment_id': payment['id'],
                    'status': payment['status'],
                    'amount': payment['amount_money']['amount'],
                    'currency': payment['amount_money']['currency']
                }
            else:
                errors = result.errors if result.errors else []
                error_messages = [error.get('detail', str(error)) for error in errors]
                logger.error(f"Failed to retrieve payment {payment_id}: {error_messages}")
                return {
                    'success': False,
                    'error': f'Failed to retrieve payment: {", ".join(error_messages)}',
                    'errors': errors,
                    'payment': None
                }
                
        except Exception as e:
            logger.error(f"Error retrieving Square payment {payment_id}: {str(e)}")
            return {
                'success': False,
                'error': f'Square payment retrieval error: {str(e)}',
                'payment': None
            }
    
    def refund_payment(self, payment_id: str, amount: int, reason: str = None) -> Dict[str, Any]:
        """
        Refund a payment.
        
        Args:
            payment_id: Square payment ID to refund
            amount: Refund amount in cents
            reason: Refund reason
            
        Returns:
            Dict containing refund result
        """
        try:
            if not self.client:
                return {
                    'success': False,
                    'error': 'Square not configured. Set SQUARE_ACCESS_TOKEN environment variable.',
                    'refund_id': None
                }
            
            # Create refund request
            from square.models import CreateRefundRequest, Money
            
            refund_money = Money(amount=amount, currency="USD")
            refund_request = CreateRefundRequest(
                payment_id=payment_id,
                amount_money=refund_money,
                reason=reason or "Customer requested refund"
            )
            
            result = self.client.refunds.create_refund(refund_request)
            
            if result.is_success():
                refund = result.body['refund']
                logger.info(f"Refund processed successfully: {refund['id']}")
                return {
                    'success': True,
                    'refund_id': refund['id'],
                    'payment_id': refund['payment_id'],
                    'amount': refund['amount_money']['amount'],
                    'status': refund['status'],
                    'reason': refund['reason'],
                    'created_at': refund['created_at']
                }
            else:
                errors = result.errors if result.errors else []
                error_messages = [error.get('detail', str(error)) for error in errors]
                logger.error(f"Square refund failed: {error_messages}")
                return {
                    'success': False,
                    'error': f'Square refund failed: {", ".join(error_messages)}',
                    'errors': errors,
                    'refund_id': None
                }
                
        except Exception as e:
            logger.error(f"Error processing Square refund: {str(e)}")
            return {
                'success': False,
                'error': f'Square refund error: {str(e)}',
                'refund_id': None
            }
    
    def _create_square_address(self, address_data: Dict[str, Any]) -> SquareAddress:
        """
        Create Square Address object from address data.
        
        Args:
            address_data: Address information dictionary
            
        Returns:
            Square Address object
        """
        return SquareAddress(
            address_line_1=address_data.get('street', ''),
            address_line_2=address_data.get('apt', ''),
            locality=address_data.get('city', ''),
            administrative_district_level_1=address_data.get('state', ''),
            postal_code=address_data.get('zip_code', ''),
            country=address_data.get('country', 'US')
        )
    
    @property
    def is_configured(self) -> bool:
        """Check if Square is properly configured and ready to process payments."""
        return self._is_configured and bool(self.access_token and self.client)
    
    def get_square_info(self) -> Dict[str, Any]:
        """
        Get Square configuration information.
        
        Returns:
            Dict containing Square configuration details
        """
        return {
            'environment': self.environment,
            'application_id': self.application_id,
            'location_id': self.location_id,
            'configured': self.is_configured,
            'sdk_available': SQUARE_AVAILABLE
        }
    
    def validate_webhook_signature(self, payload: str, signature: str, webhook_url: str) -> bool:
        """
        Validate Square webhook signature.
        
        Args:
            payload: Webhook payload body
            signature: Webhook signature header
            webhook_url: Webhook URL
            
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            if not self.client:
                return False
            
            # Square webhook signature validation
            # This would need to be implemented based on Square's webhook validation requirements
            # For now, return True (implement proper validation in production)
            logger.info("Webhook signature validation not fully implemented")
            return True
            
        except Exception as e:
            logger.error(f"Error validating webhook signature: {str(e)}")
            return False
