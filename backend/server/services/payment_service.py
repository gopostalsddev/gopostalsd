"""
Payment Service for Go Postal SD Application

This service provides payment processing functionality using various payment providers.
It acts as a facade over payment adapters, providing a consistent interface for payment operations.
"""

import logging
from typing import Dict, Any, Optional
from server.thirdparty.square import SquareAdapter

logger = logging.getLogger(__name__)


class PaymentService:
    """
    Service for handling payment operations.
    
    This service provides a unified interface for payment processing,
    supporting multiple payment providers through adapters.
    """
    
    def __init__(self, provider: str = "square"):
        """
        Initialize payment service with specified provider.
        
        Args:
            provider: Payment provider ('square', 'stripe', 'paypal', etc.)
        """
        self.provider = provider.lower()
        self.client = None
        
        try:
            if self.provider == 'square':
                self.client = SquareAdapter()
                provider_name = "Square"
            else:
                logger.error(f"Unknown payment provider: {self.provider}")
                return
            
            if self.client.is_configured:
                logger.info(f"Payment service initialized successfully with {provider_name}")
            else:
                logger.warning(f"Payment service initialized with {provider_name} but not configured")
                
        except Exception as e:
            logger.error(f"Failed to initialize {self.provider} payment service: {str(e)}")
            self.client = None
    
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
        Process a payment using the configured provider.
        
        Args:
            amount: Payment amount in cents (e.g., 1000 = $10.00)
            currency: Currency code (default: USD)
            source_id: Payment source ID (card nonce, token, etc.)
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
        if not self.client:
            return {
                'success': False, 
                'error': f'Payment service not configured. Set {self.provider.upper()}_ACCESS_TOKEN environment variable.'
            }
        
        return self.client.process_payment(
            amount=amount,
            currency=currency,
            source_id=source_id,
            idempotency_key=idempotency_key,
            buyer_email=buyer_email,
            buyer_phone=buyer_phone,
            shipping_address=shipping_address,
            billing_address=billing_address,
            order_id=order_id,
            note=note
        )
    
    def get_payment(self, payment_id: str) -> Dict[str, Any]:
        """
        Retrieve payment details by ID.
        
        Args:
            payment_id: Payment ID
            
        Returns:
            Dict containing payment details or error information
        """
        if not self.client:
            return {
                'success': False, 
                'error': f'Payment service not configured. Set {self.provider.upper()}_ACCESS_TOKEN environment variable.'
            }
        
        return self.client.get_payment(payment_id)
    
    def refund_payment(self, payment_id: str, amount: int, reason: str = None) -> Dict[str, Any]:
        """
        Refund a payment.
        
        Args:
            payment_id: Payment ID to refund
            amount: Refund amount in cents
            reason: Refund reason
            
        Returns:
            Dict containing refund result
        """
        if not self.client:
            return {
                'success': False, 
                'error': f'Payment service not configured. Set {self.provider.upper()}_ACCESS_TOKEN environment variable.'
            }
        
        return self.client.refund_payment(payment_id, amount, reason)
    
    @property
    def is_configured(self) -> bool:
        """Check if payment service is properly configured."""
        return self.client and self.client.is_configured
    
    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get payment provider information.
        
        Returns:
            Dict containing provider configuration details
        """
        info = {
            'provider': self.provider,
            'configured': self.is_configured
        }
        
        if self.client and hasattr(self.client, 'get_square_info'):
            info.update(self.client.get_square_info())
        
        return info
    
    def validate_webhook(self, payload: str, signature: str, webhook_url: str) -> bool:
        """
        Validate payment webhook signature.
        
        Args:
            payload: Webhook payload body
            signature: Webhook signature header
            webhook_url: Webhook URL
            
        Returns:
            True if signature is valid, False otherwise
        """
        if not self.client:
            return False
        
        if hasattr(self.client, 'validate_webhook_signature'):
            return self.client.validate_webhook_signature(payload, signature, webhook_url)
        
        return False
