# SMTPAdapter Documentation

## Overview

The `SMTPAdapter` is a third-party integration adapter that provides email sending capabilities using standard SMTP (Simple Mail Transfer Protocol). This adapter supports any SMTP server, including Gmail, Outlook, Yahoo, and custom SMTP servers.

## Configuration

### Environment Variables

```bash
# Required - SMTP Server Configuration
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Optional - SMTP Server Settings (defaults provided)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true

# Optional - Email Configuration (defaults provided)
FROM_EMAIL=noreply@gopostalsd.com
FROM_NAME=Go Postal SD
```

### Common SMTP Providers

#### Gmail
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password  # Not your regular password!
```

#### Outlook/Hotmail
```bash
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USERNAME=your_email@outlook.com
SMTP_PASSWORD=your_password
```

#### Yahoo
```bash
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USERNAME=your_email@yahoo.com
SMTP_PASSWORD=your_app_password
```

#### Custom SMTP Server
```bash
SMTP_SERVER=your-smtp-server.com
SMTP_PORT=587  # or 465 for SSL
SMTP_USE_TLS=true  # or false for SSL
SMTP_USERNAME=your_username
SMTP_PASSWORD=your_password
```

## Gmail Setup Guide

### 1. Enable 2-Factor Authentication
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Step Verification
3. This is required to generate app passwords

### 2. Generate App Password
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Click "App passwords" under "Signing in to Google"
3. Select "Mail" and your device
4. Copy the generated 16-character password
5. Use this password as `SMTP_PASSWORD` (not your regular Gmail password)

### 3. Configure Environment Variables
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_16_character_app_password
```

## Features

- **Universal Compatibility**: Works with any SMTP server
- **TLS/SSL Support**: Secure email transmission
- **HTML & Text Support**: Send both HTML and plain text emails
- **Error Handling**: Comprehensive SMTP error reporting
- **No External Dependencies**: Uses Python's built-in `smtplib`
- **Flexible Configuration**: Support for various SMTP providers

## Core Functionality

### 1. Basic Email Sending

```python
from server.thirdparty.smtp import SMTPAdapter

# Initialize adapter
smtp_adapter = SMTPAdapter()

# Send simple email
result = smtp_adapter.send_email(
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

### 2. Custom SMTP Configuration

```python
# Initialize with custom SMTP settings
smtp_adapter = SMTPAdapter(
    smtp_server="smtp.custom-server.com",
    smtp_port=587,
    username="custom@example.com",
    password="custom_password",
    use_tls=True,
    from_email="noreply@example.com",
    from_name="Custom Service"
)
```

### 3. Configuration Status

```python
# Check if adapter is properly configured
if smtp_adapter.is_configured:
    print("SMTP is ready to send emails")
else:
    print("SMTP not configured - check SMTP_USERNAME and SMTP_PASSWORD")
```

### 4. Get Configuration Info

```python
# Get SMTP configuration details
smtp_info = smtp_adapter.get_smtp_info()
print(f"Server: {smtp_info['server']}:{smtp_info['port']}")
print(f"TLS: {smtp_info['use_tls']}")
print(f"From: {smtp_info['from_name']} <{smtp_info['from_email']}>")
```

### 5. Reply-To Functionality

The SMTPAdapter supports reply-to addresses for better email management:

```python
# Send email with custom reply-to
result = smtp_adapter.send_email(
    to_email="customer@example.com",
    subject="Order Confirmation",
    text_content="Your order has been confirmed.",
    reply_to="orders@gopostalsd.com"  # Replies will go to orders department
)

# If no reply_to is provided, it defaults to the FROM_EMAIL
result = smtp_adapter.send_email(
    to_email="customer@example.com",
    subject="Order Confirmation", 
    text_content="Your order has been confirmed."
    # reply_to defaults to FROM_EMAIL environment variable
)
```

**Reply-To Behavior:**
- If `reply_to` parameter is provided, it will be used
- If `reply_to` is `None` or not provided, defaults to `FROM_EMAIL`
- Reply-To header is automatically added to the email message
- Recipients can reply directly to the specified address

## Response Format

All email sending methods return a standardized response:

### Success Response
```python
{
    'success': True,
    'message': 'Email sent successfully via SMTP',
    'recipient': 'user@example.com',
    'provider': 'SMTP'
}
```

### Error Response
```python
{
    'success': False,
    'error': 'SMTP authentication failed: Invalid credentials',
    'recipient': 'user@example.com',
    'provider': 'SMTP'
}
```

## Integration with EmailService

The SMTPAdapter is designed to work seamlessly with the EmailService:

```python
from server.services.email_service import EmailService

# Initialize email service with SMTP
email_service = EmailService()
email_service.init_app(app, provider='smtp')

# Send verification email
result = email_service.send_verification_email(
    email="user@example.com",
    first_name="John",
    token="verification-token-123"
)
```

## Error Handling

The adapter handles various SMTP error scenarios:

### 1. Authentication Errors
- Invalid username/password
- Account locked or suspended
- 2FA not properly configured

### 2. Connection Errors
- Network connectivity issues
- SMTP server unavailable
- Firewall blocking SMTP ports

### 3. Email Format Errors
- Invalid email addresses
- Malformed email headers
- Content encoding issues

### 4. Example Error Handling
```python
result = smtp_adapter.send_email(
    to_email="invalid-email",
    subject="Test",
    text_content="Test message"
)

if not result['success']:
    if 'authentication' in result['error'].lower():
        print("Check your SMTP username and password")
    elif 'connection' in result['error'].lower():
        print("Check network connectivity and SMTP server")
    else:
        print(f"Email failed: {result['error']}")
```

## Logging and Monitoring

The adapter provides detailed logging:

```python
import logging

# Enable debug logging
logging.getLogger('server.thirdparty.smtp').setLevel(logging.DEBUG)
```

### Log Events
- **Configuration**: SMTP server setup and validation
- **Connection**: SMTP server connection attempts
- **Authentication**: Login success/failure
- **Email Sending**: Success/failure with details
- **Errors**: Detailed error information

## Best Practices

### 1. Security
- Use app passwords for Gmail (not regular passwords)
- Enable 2FA on email accounts
- Use TLS encryption (`SMTP_USE_TLS=true`)
- Store credentials securely in environment variables

### 2. Email Content
- Always provide both HTML and text content
- Use proper email formatting
- Test email rendering across different clients
- Include proper headers and encoding

### 3. Error Handling
- Always check the `success` field in responses
- Implement retry logic for transient failures
- Log errors for monitoring and debugging
- Provide user-friendly error messages

### 4. Performance
- Reuse SMTP connections when possible
- Implement connection pooling for high volume
- Monitor SMTP server performance
- Consider rate limiting for bulk operations

## Testing

### Unit Testing
```python
import unittest
from unittest.mock import patch, MagicMock
from server.thirdparty.smtp import SMTPAdapter

class TestSMTPAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = SMTPAdapter(
            username="test@example.com",
            password="test_password"
        )
    
    @patch('smtplib.SMTP')
    def test_send_email_success(self, mock_smtp):
        # Mock successful SMTP connection
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        result = self.adapter.send_email(
            to_email="test@example.com",
            subject="Test",
            text_content="Test message"
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['provider'], 'SMTP')
```

### Integration Testing
```python
def test_smtp_integration():
    """Test actual SMTP server integration."""
    adapter = SMTPAdapter()
    
    if not adapter.is_configured:
        pytest.skip("SMTP not configured")
    
    result = adapter.send_email(
        to_email="test@example.com",
        subject="Integration Test",
        text_content="This is a test email",
        html_content="<h1>Test Email</h1>"
    )
    
    assert result['success'] == True
    assert result['recipient'] == "test@example.com"
    assert result['provider'] == "SMTP"
```

## Troubleshooting

### Common Issues

1. **"SMTP not configured"**
   - Verify `SMTP_USERNAME` and `SMTP_PASSWORD` are set
   - Check environment variable names and values
   - Ensure credentials are not empty

2. **"Authentication failed"**
   - Verify username and password are correct
   - For Gmail, ensure you're using an app password
   - Check if 2FA is properly configured
   - Verify account is not locked

3. **"Connection failed"**
   - Check network connectivity
   - Verify SMTP server address and port
   - Check firewall settings
   - Ensure SMTP server is running

4. **"Email sending failed"**
   - Check recipient email address format
   - Verify sender email address is valid
   - Check email content for issues
   - Review SMTP server logs

### Debug Steps

1. **Check Configuration**
   ```python
   adapter = SMTPAdapter()
   print(f"Configured: {adapter.is_configured}")
   smtp_info = adapter.get_smtp_info()
   print(f"SMTP Info: {smtp_info}")
   ```

2. **Test SMTP Connection**
   ```python
   import smtplib
   
   try:
       server = smtplib.SMTP('smtp.gmail.com', 587)
       server.starttls()
       server.login('your_email@gmail.com', 'your_app_password')
       print("SMTP connection successful")
       server.quit()
   except Exception as e:
       print(f"SMTP connection failed: {e}")
   ```

3. **Check Email Provider Status**
   - Gmail: Check [Gmail Status](https://www.google.com/appsstatus)
   - Outlook: Check [Office 365 Status](https://status.office365.com/)
   - Yahoo: Check [Yahoo Status](https://status.yahoo.com/)

## Performance Considerations

- **Connection Overhead**: SMTP connections have setup overhead
- **Rate Limits**: Email providers have sending limits
- **Network Latency**: SMTP performance depends on network conditions
- **Server Load**: SMTP server performance affects sending speed

## Security Considerations

- **Credential Security**: Never commit passwords to version control
- **TLS Encryption**: Always use TLS for secure transmission
- **App Passwords**: Use app-specific passwords for Gmail
- **Access Control**: Limit SMTP account permissions
- **Audit Logging**: Log all email sending activities

## Comparison with MailerSend

| Feature | SMTP | MailerSend |
|---------|------|------------|
| **Setup Complexity** | Medium | Low |
| **Deliverability** | Good | Excellent |
| **Analytics** | None | Built-in |
| **Rate Limits** | Provider-dependent | Generous |
| **Cost** | Free (with limits) | Paid |
| **Dependencies** | None | External API |
| **Reliability** | Good | Excellent |

## Future Enhancements

Potential improvements for the SMTPAdapter:

1. **Connection Pooling**: Reuse SMTP connections
2. **Batch Sending**: Support for bulk email operations
3. **Delivery Tracking**: Basic delivery confirmation
4. **Template Support**: Email template management
5. **Advanced Authentication**: OAuth2 support for Gmail
6. **Performance Monitoring**: SMTP performance metrics
