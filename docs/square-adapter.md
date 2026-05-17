# Square Payment Adapter Documentation

## Overview

The SquareAdapter provides a wrapper around the Square Payment API for processing payments in the Go Postal SD application. It follows the Adapter pattern to provide a consistent interface for payment processing, handling authentication, payment processing, refunds, and webhook validation.

## Features

- **Payment Processing**: Process payments using Square's Payment API
- **Payment Retrieval**: Get payment details by payment ID
- **Refund Processing**: Process refunds for existing payments
- **Webhook Validation**: Validate Square webhook signatures
- **Address Handling**: Support for shipping and billing addresses
- **Error Handling**: Comprehensive error reporting and logging
- **Environment Support**: Sandbox and production environments

## Configuration

### Environment Variables

Set the following environment variables to configure Square:

```bash
# Required
SQUARE_ACCESS_TOKEN=your_square_access_token
SQUARE_APPLICATION_ID=your_square_application_id
SQUARE_LOCATION_ID=your_square_location_id

# Optional
SQUARE_ENVIRONMENT=sandbox  # or 'production'
```

### Square Developer Setup

1. **Create Square Developer Account**:
   - Visit [Square Developer Dashboard](https://developer.squareup.com/)
   - Sign in or create a new account

2. **Create Application**:
   - Create a new application to get your Application ID and Access Token
   - Note your Application ID and Access Token

3. **Get Location ID**:
   - In your Square Dashboard, go to Locations
   - Copy your Location ID

4. **Install Square SDK**:
   ```bash
   pip install squareup
   ```

## Core Functionality

### 1. Basic Payment Processing

```python
from server.thirdparty.square import SquareAdapter

# Initialize adapter
square_adapter = SquareAdapter()

# Process payment
result = square_adapter.process_payment(
    amount=2500,  # $25.00 in cents
    currency="USD",
    source_id="cnon:card-nonce-ok",  # Card nonce from Square Web Payments SDK
    buyer_email="customer@example.com",
    order_id="order_123"
)

if result['success']:
    print(f"Payment successful: {result['payment_id']}")
else:
    print(f"Payment failed: {result['error']}")
```

### 2. Payment with Addresses

```python
# Process payment with shipping and billing addresses
result = square_adapter.process_payment(
    amount=5000,  # $50.00
    currency="USD",
    source_id="cnon:card-nonce-ok",
    buyer_email="customer@example.com",
    shipping_address={
        'street': '123 Main St',
        'city': 'San Diego',
        'state': 'CA',
        'zip_code': '92101',
        'country': 'US',
        'apt': 'Suite 100'
    },
    billing_address={
        'street': '456 Oak Ave',
        'city': 'San Diego', 
        'state': 'CA',
        'zip_code': '92102',
        'country': 'US'
    },
    order_id="order_456",
    note="Printing services order"
)
```

### 3. Payment Retrieval

```python
# Get payment details
result = square_adapter.get_payment("payment_id_here")

if result['success']:
    payment = result['payment']
    print(f"Payment Status: {payment['status']}")
    print(f"Amount: ${payment['amount_money']['amount'] / 100}")
else:
    print(f"Error: {result['error']}")
```

### 4. Refund Processing

```python
# Process refund
result = square_adapter.refund_payment(
    payment_id="payment_id_here",
    amount=1000,  # Refund $10.00
    reason="Customer requested refund"
)

if result['success']:
    print(f"Refund successful: {result['refund_id']}")
else:
    print(f"Refund failed: {result['error']}")
```

### 5. Configuration Status

```python
# Check if adapter is properly configured
if square_adapter.is_configured:
    print("Square adapter is ready to process payments")
else:
    print("Square adapter not configured - check environment variables")

# Get configuration info
info = square_adapter.get_square_info()
print(f"Environment: {info['environment']}")
print(f"Location ID: {info['location_id']}")
```

## Integration with PaymentService

The SquareAdapter is designed to work seamlessly with the PaymentService:

```python
from server.services.payment_service import PaymentService

# Initialize payment service with Square
payment_service = PaymentService(provider='square')

# Process payment
result = payment_service.process_payment(
    amount=3000,  # $30.00
    currency="USD",
    source_id="cnon:card-nonce-ok",
    buyer_email="customer@example.com"
)
```

## API Endpoints

### Process Payment
```http
POST /api/payments/process
Content-Type: application/json
Authorization: Bearer <token>

{
    "amount": 2500,
    "currency": "USD",
    "source_id": "cnon:card-nonce-ok",
    "buyer_email": "customer@example.com",
    "order_id": "order_123"
}
```

### Get Payment
```http
GET /api/payments/{payment_id}
Authorization: Bearer <token>
```

### Process Refund (Admin Only)
```http
POST /api/payments/refund
Content-Type: application/json
Authorization: Bearer <admin_token>

{
    "payment_id": "payment_id_here",
    "amount": 1000,
    "reason": "Customer requested refund"
}
```

### Payment Status
```http
GET /api/payments/status
```

## Response Format

### Success Response
```python
{
    'success': True,
    'payment_id': 'payment_123',
    'status': 'COMPLETED',
    'amount': 2500,
    'currency': 'USD',
    'created_at': '2024-01-01T12:00:00Z',
    'receipt_url': 'https://squareup.com/receipt/...',
    'order_id': 'order_123',
    'idempotency_key': 'gopostalsd_20240101_120000_2500'
}
```

### Error Response
```python
{
    'success': False,
    'error': 'Square payment failed: Card declined',
    'errors': [
        {
            'category': 'PAYMENT_METHOD_ERROR',
            'code': 'CARD_DECLINED',
            'detail': 'Card was declined'
        }
    ],
    'payment_id': None
}
```

## Frontend Integration

### Square Web Payments SDK

To collect payment information securely on the frontend:

```html
<!-- Include Square Web Payments SDK -->
<script type="text/javascript" src="https://sandbox.web.squarecdn.com/v1/square.js"></script>
```

```javascript
// Initialize Square Web Payments SDK
const payments = Square.payments('your_application_id', 'your_location_id');

// Create card payment method
const card = await payments.card();

// Attach to form
await card.attach('#card-container');

// Handle form submission
document.getElementById('payment-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    
    try {
        const result = await card.tokenize();
        if (result.status === 'OK') {
            // Send token to backend
            const response = await fetch('/api/payments/process', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${userToken}`
                },
                body: JSON.stringify({
                    amount: 2500,
                    source_id: result.token,
                    buyer_email: 'customer@example.com'
                })
            });
            
            const paymentResult = await response.json();
            if (paymentResult.success) {
                console.log('Payment successful:', paymentResult.payment_id);
            }
        }
    } catch (error) {
        console.error('Payment error:', error);
    }
});
```

## Error Handling

### Common Error Types

1. **Configuration Errors**:
   - Missing access token
   - Invalid environment
   - SDK not available

2. **Payment Errors**:
   - Card declined
   - Insufficient funds
   - Invalid card information
   - Processing errors

3. **Validation Errors**:
   - Missing required fields
   - Invalid amount
   - Invalid currency

### Error Handling Example

```python
try:
    result = square_adapter.process_payment(
        amount=amount,
        source_id=source_id,
        buyer_email=buyer_email
    )
    
    if result['success']:
        # Payment successful
        payment_id = result['payment_id']
        # Process successful payment
    else:
        # Handle payment failure
        error_message = result['error']
        errors = result.get('errors', [])
        
        for error in errors:
            if error.get('code') == 'CARD_DECLINED':
                # Handle card declined
                pass
            elif error.get('code') == 'INSUFFICIENT_FUNDS':
                # Handle insufficient funds
                pass
                
except Exception as e:
    # Handle unexpected errors
    logger.error(f"Unexpected payment error: {str(e)}")
```

## Testing

### Sandbox Environment

Square provides a sandbox environment for testing:

```python
# Use sandbox environment
square_adapter = SquareAdapter(environment='sandbox')

# Test with sandbox card nonces
test_nonces = {
    'success': 'cnon:card-nonce-ok',
    'decline': 'cnon:card-nonce-declined',
    'insufficient_funds': 'cnon:card-nonce-insufficient-funds'
}
```

### Unit Testing

```python
import unittest
from unittest.mock import patch, MagicMock
from server.thirdparty.square import SquareAdapter

class TestSquareAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = SquareAdapter(access_token="test_token")
    
    @patch('server.thirdparty.square.SquareClient')
    def test_process_payment_success(self, mock_client_class):
        # Mock successful payment response
        mock_response = MagicMock()
        mock_response.is_success.return_value = True
        mock_response.body = {
            'payment': {
                'id': 'payment_123',
                'status': 'COMPLETED',
                'amount_money': {'amount': 2500, 'currency': 'USD'},
                'created_at': '2024-01-01T12:00:00Z'
            }
        }
        
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.payments.create_payment.return_value = mock_response
        
        result = self.adapter.process_payment(
            amount=2500,
            source_id="test_nonce"
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['payment_id'], 'payment_123')
```

## Security Considerations

### 1. Token Security
- Never expose access tokens in client-side code
- Use environment variables for sensitive configuration
- Rotate access tokens regularly

### 2. Webhook Security
- Validate webhook signatures
- Use HTTPS for webhook endpoints
- Implement proper authentication

### 3. PCI Compliance
- Never store card information
- Use Square's secure tokenization
- Follow PCI DSS guidelines

### 4. Error Handling
- Don't expose sensitive error details to clients
- Log errors securely
- Implement proper error responses

## Best Practices

### 1. Payment Processing
- Always use idempotency keys
- Handle partial failures gracefully
- Implement retry logic for transient errors

### 2. User Experience
- Provide clear error messages
- Show loading states during processing
- Implement proper form validation

### 3. Monitoring
- Log all payment attempts
- Monitor success/failure rates
- Set up alerts for payment failures

### 4. Testing
- Test with various card types
- Test error scenarios
- Use sandbox environment for development

## Troubleshooting

### Common Issues

1. **"Square SDK not available"**:
   - Install Square SDK: `pip install squareup`
   - Check Python environment

2. **"Square not configured"**:
   - Set SQUARE_ACCESS_TOKEN environment variable
   - Verify access token is valid

3. **"Card declined"**:
   - Check card information
   - Verify card has sufficient funds
   - Check Square's decline reasons

4. **"Invalid location ID"**:
   - Verify SQUARE_LOCATION_ID is correct
   - Check location is active in Square Dashboard

### Debug Steps

1. **Check Configuration**:
   ```python
   info = square_adapter.get_square_info()
   print(f"Configured: {info['configured']}")
   print(f"Environment: {info['environment']}")
   ```

2. **Test Connection**:
   ```python
   # Try a simple API call
   result = square_adapter.get_payment("test_payment_id")
   ```

3. **Check Logs**:
   - Review application logs for Square API errors
   - Check Square Developer Dashboard for API logs

## Performance Considerations

### 1. Connection Pooling
- Square SDK handles connection pooling automatically
- No additional configuration needed

### 2. Rate Limits
- Square has API rate limits
- Implement exponential backoff for retries
- Monitor API usage

### 3. Timeout Handling
- Set appropriate timeouts for API calls
- Handle timeout errors gracefully
- Implement retry logic

## Future Enhancements

### Planned Features
- Support for additional payment methods
- Recurring payment support
- Multi-currency support
- Advanced reporting features

### Integration Opportunities
- Order management system
- Inventory management
- Customer relationship management
- Analytics and reporting
