# MailerSendAdapter Documentation

## Overview

The `MailerSendAdapter` is a third-party integration adapter that provides email sending capabilities using the MailerSend API. MailerSend is a transactional email service that offers high deliverability, analytics, and professional email features.

## Configuration

### Environment Variables

```bash
# Required - MailerSend API Configuration
MAILERSEND_API_KEY=your_mailersend_api_key_here

# Optional - Email Configuration (defaults provided)
FROM_EMAIL=noreply@gopostalsd.com
FROM_NAME=Go Postal SD
```

### Getting MailerSend API Key

1. **Create Account**: Sign up at [MailerSend](https://www.mailersend.com/)
2. **Verify Domain**: Add and verify your sending domain
3. **Generate API Key**: Create an API key in the MailerSend dashboard
4. **Set Environment Variable**: Add the API key to your environment

## Features

- **High Deliverability**: Professional email infrastructure
- **HTML & Text Support**: Send both HTML and plain text emails
- **Analytics**: Track email delivery and engagement
- **Rate Limiting**: Built-in rate limiting protection
- **Error Handling**: Comprehensive error reporting
- **Template Support**: Support for email templates (via MailerSend dashboard)

## Core Functionality

### 1. Basic Email Sending

```python
from server.thirdparty.mailersend import MailerSendAdapter

# Initialize adapter
mailer_adapter = MailerSendAdapter()

# Send simple email
result = mailer_adapter.send_email(
    to_email="user@example.com",
    subject="Welcome to Go Postal SD",
    text_content="Welcome! Thank you for joining us.",
    html_content="<h1>Welcome!</h1><p>Thank you for joining us.</p>",
    reply_to="support@gopostalsd.com"  # Optional reply-to address
)

if result['success']:
    print("Email sent successfully")
else:
    print(f"Email failed: {result['error']}")
```

**Note**: The MailerSendAdapter uses the official MailerSend Python SDK with `MailerSendClient` and `Email` classes for reliable email delivery.

### 2. Configuration Status

```python
# Check if adapter is properly configured
if mailer_adapter.is_configured:
    print("MailerSend is ready to send emails")
else:
    print("MailerSend not configured - check MAILERSEND_API_KEY")
```

### 3. Get Configuration Info

```python
# Get configured email addresses
from_email = mailer_adapter.get_from_email()
from_name = mailer_adapter.get_from_name()

print(f"Emails will be sent from: {from_name} <{from_email}>")
```

## Response Format

All email sending methods return a standardized response:

### Success Response
```python
{
    'success': True,
    'message': 'Email sent successfully',
    'status_code': 202,
    'recipient': 'user@example.com'
}
```

### Error Response
```python
{
    'success': False,
    'error': 'MailerSend API error: 401',
    'status_code': 401,
    'recipient': 'user@example.com'
}
```

## Technical Implementation

The MailerSendAdapter uses the official MailerSend Python SDK:

```python
from mailersend import MailerSendClient, Email

# Client initialization
self.client = MailerSendClient(api_key=self.api_key)

# Email creation and sending
email = Email()
email.set_from(self.from_email, self.from_name)
email.set_to(to_email)
email.set_subject(subject)
email.set_text(text_content)
if html_content:
    email.set_html(html_content)

# Add reply-to (defaults to from_email if not provided)
reply_to_email = reply_to or self.from_email
email.set_reply_to(reply_to_email)

# Send email
response = self.client.send(email)
```

## Integration with EmailService

The MailerSendAdapter is designed to work seamlessly with the EmailService:

```python
from server.services.email_service import EmailService

# Initialize email service with MailerSend
email_service = EmailService()
email_service.init_app(app, provider='mailersend')

# Send verification email
result = email_service.send_verification_email(
    email="user@example.com",
    first_name="John",
    token="verification-token-123"
)
```

## Email Types Supported

### 1. Email Verification
```python
result = email_service.send_verification_email(
    email="user@example.com",
    first_name="John",
    token="verification-token-123"
)
```

### 2. Password Reset
```python
result = email_service.send_password_reset_email(
    email="user@example.com",
    first_name="John",
    token="reset-token-456"
)
```

### 3. Contact Form
```python
result = email_service.send_contact_email(
    name="John Doe",
    email="john@example.com",
    phone="555-1234",
    subject="Inquiry about services",
    message="I would like to know more about your services."
)
```

## Error Handling

The adapter handles various error scenarios:

### 1. Configuration Errors
- Missing API key
- Invalid API key format
- Network connectivity issues

### 2. API Errors
- Rate limiting (429)
- Authentication failures (401)
- Invalid email addresses (400)
- Server errors (5xx)

### 3. Example Error Handling
```python
result = mailer_adapter.send_email(
    to_email="invalid-email",
    subject="Test",
    text_content="Test message"
)

if not result['success']:
    if 'authentication' in result['error'].lower():
        print("Check your MailerSend API key")
    elif 'rate limit' in result['error'].lower():
        print("Rate limit exceeded - wait before retrying")
    else:
        print(f"Email failed: {result['error']}")
```

## Logging and Monitoring

The adapter provides detailed logging:

```python
import logging

# Enable debug logging
logging.getLogger('server.thirdparty.mailersend').setLevel(logging.DEBUG)
```

### Log Events
- **Authentication**: API key validation
- **Email Sending**: Success/failure with details
- **API Errors**: Detailed error information
- **Configuration**: Setup and validation status

## Best Practices

### 1. Email Content
- Always provide both HTML and text content
- Use proper email formatting
- Include unsubscribe links for marketing emails
- Test email rendering across different clients

### 2. Error Handling
- Always check the `success` field in responses
- Implement retry logic for transient failures
- Log errors for monitoring and debugging
- Provide user-friendly error messages

### 3. Rate Limiting
- Respect MailerSend rate limits
- Implement exponential backoff for retries
- Monitor API usage in MailerSend dashboard

### 4. Security
- Store API keys securely in environment variables
- Never log sensitive information
- Use HTTPS for all API communications
- Regularly rotate API keys

## Testing

### Unit Testing
```python
import unittest
from unittest.mock import patch, MagicMock
from server.thirdparty.mailersend import MailerSendAdapter

class TestMailerSendAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = MailerSendAdapter(api_key="test_key")
    
    @patch('server.thirdparty.mailersend.MailerSendClient')
    @patch('server.thirdparty.mailersend.Email')
    def test_send_email_success(self, mock_email_class, mock_client_class):
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 202
        
        # Mock client and email instances
        mock_client = MagicMock()
        mock_email = MagicMock()
        mock_client_class.return_value = mock_client
        mock_email_class.return_value = mock_email
        mock_client.send.return_value = mock_response
        
        result = self.adapter.send_email(
            to_email="test@example.com",
            subject="Test",
            text_content="Test message"
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['status_code'], 202)
```

### Integration Testing
```python
def test_mailersend_integration():
    """Test actual MailerSend API integration."""
    adapter = MailerSendAdapter()
    
    if not adapter.is_configured:
        pytest.skip("MailerSend not configured")
    
    result = adapter.send_email(
        to_email="test@example.com",
        subject="Integration Test",
        text_content="This is a test email",
        html_content="<h1>Test Email</h1>"
    )
    
    assert result['success'] == True
    assert result['recipient'] == "test@example.com"
```

## Troubleshooting

### Common Issues

1. **"MailerSend not configured"**
   - Verify `MAILERSEND_API_KEY` is set
   - Check API key format and validity
   - Ensure network connectivity

2. **"Authentication failed"**
   - Verify API key is correct
   - Check if API key has proper permissions
   - Ensure account is active

3. **"Email sending failed"**
   - Check recipient email address format
   - Verify sender domain is verified in MailerSend
   - Check MailerSend service status

4. **Rate limiting errors**
   - Implement exponential backoff
   - Monitor API usage in dashboard
   - Consider upgrading MailerSend plan

### Debug Steps

1. **Check Configuration**
   ```python
   adapter = MailerSendAdapter()
   print(f"Configured: {adapter.is_configured}")
   print(f"From Email: {adapter.get_from_email()}")
   ```

2. **Test API Connection**
   ```python
   # Send test email
   result = adapter.send_email(
       to_email="your-email@example.com",
       subject="Test",
       text_content="Test message"
   )
   print(f"Result: {result}")
   ```

3. **Check MailerSend Dashboard**
   - Log into MailerSend dashboard
   - Check API usage and limits
   - Review email delivery logs
   - Verify domain authentication

## Performance Considerations

- **API Latency**: MailerSend API typically responds in 100-500ms
- **Rate Limits**: Vary by plan (check MailerSend documentation)
- **Batch Sending**: Consider batch operations for high volume
- **Caching**: Cache configuration to avoid repeated API key validation

## Security Considerations

- **API Key Security**: Never commit API keys to version control
- **Environment Variables**: Use secure environment variable management
- **HTTPS Only**: All API communications use HTTPS
- **Access Control**: Limit API key permissions to minimum required
- **Audit Logging**: Log all email sending activities for security auditing

## Future Enhancements

Potential improvements for the MailerSendAdapter:

1. **Template Management**: Direct template creation and management
2. **Analytics Integration**: Real-time delivery and engagement metrics
3. **Webhook Support**: Real-time delivery status updates
4. **Batch Operations**: Support for bulk email sending
5. **A/B Testing**: Built-in email content testing
6. **Advanced Personalization**: Dynamic content based on user data
