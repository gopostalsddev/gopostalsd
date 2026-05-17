# Documentation Changelog

## Recent Updates

### 2024-01-XX - Square Payment Adapter Added

**Changes Made:**
- Added SquareAdapter for Square Payment API integration
- Created PaymentService as a facade over payment adapters
- Added payment routes with authentication and admin controls
- Implemented comprehensive payment processing, refunds, and webhook handling
- Added Square SDK to requirements.txt

**Technical Implementation:**
- SquareAdapter: Wraps Square Payment API with consistent interface
- PaymentService: Provides unified payment processing across providers
- Payment Routes: RESTful API endpoints for payment operations
- Webhook Support: Square webhook validation and processing
- Address Handling: Support for shipping and billing addresses

**API Endpoints Added:**
- `POST /api/payments/process` - Process payments (authenticated users)
- `GET /api/payments/{payment_id}` - Get payment details (authenticated users)
- `POST /api/payments/refund` - Process refunds (admin only)
- `POST /api/payments/webhook` - Handle Square webhooks
- `GET /api/payments/status` - Check payment service status

**Documentation Updated:**
- `docs/square-adapter.md` - Comprehensive Square adapter documentation
- `docs/CHANGELOG.md` - Documented the new payment system
- `docs/api-endpoints.md` - Added payment endpoints (to be updated)

**Files Created:**
- `backend/server/thirdparty/square.py` - Square adapter implementation
- `backend/server/services/payment_service.py` - Payment service facade
- `backend/server/routes/payment_routes.py` - Payment API routes
- `docs/square-adapter.md` - Square adapter documentation

**Files Modified:**
- `backend/server/routes/__init__.py` - Added payment routes registration
- `backend/requirements.txt` - Added squareup==35.0.0 dependency

**Configuration Required:**
```bash
SQUARE_ACCESS_TOKEN=your_square_access_token
SQUARE_APPLICATION_ID=your_square_application_id
SQUARE_LOCATION_ID=your_square_location_id
SQUARE_ENVIRONMENT=sandbox  # or 'production'
```

**Impact:**
- Complete payment processing integration with Square
- Secure payment handling with proper authentication
- Admin-controlled refund processing
- Webhook support for real-time payment updates
- Consistent adapter pattern for future payment providers

---

### 2024-01-XX - Reply-To Email Support Added

**Changes Made:**
- Added reply-to functionality to all email adapters and services
- MailerSendAdapter now supports `reply_to` parameter in `send_email()` method
- SMTPAdapter now supports `reply_to` parameter in `send_email()` method
- EmailService updated to pass through reply-to parameter to all email methods
- Reply-to defaults to `FROM_EMAIL` environment variable when not specified
- Contact form emails now use customer's email as reply-to for better communication

**Technical Implementation:**
- MailerSendAdapter: Uses `email.set_reply_to(reply_to_email)` method
- SMTPAdapter: Sets `msg['Reply-To'] = reply_to_email` header
- EmailService: All methods (`send_verification_email`, `send_password_reset_email`, `send_contact_email`) now support `reply_to` parameter
- Contact emails: Reply-to defaults to customer's email for direct communication

**Documentation Updated:**
- `docs/mailersend-adapter.md` - Added reply-to examples and technical implementation
- `docs/smtp-adapter.md` - Added reply-to functionality section with examples
- `docs/CHANGELOG.md` - Documented the new feature

**Files Modified:**
- `backend/server/thirdparty/mailersend.py` - Added reply-to support
- `backend/server/thirdparty/smtp.py` - Added reply-to support  
- `backend/server/services/email_service.py` - Updated all email methods
- `docs/mailersend-adapter.md` - Updated documentation
- `docs/smtp-adapter.md` - Updated documentation

**Impact:**
- Better email communication flow
- Replies go to appropriate addresses (customer email for contact forms)
- Maintains FROM_EMAIL as default when no reply-to specified
- Consistent behavior across all email providers

---

### 2024-01-XX - MailerSendAdapter API Update

**Changes Made:**
- Updated MailerSendAdapter to use correct MailerSend Python SDK API
- Changed from `MailerSendSDK` to `MailerSendClient` and `Email` classes
- Fixed import statements: `from mailersend import MailerSendClient, Email`
- Updated email sending method to use proper SDK methods:
  - `email.set_from()`, `email.set_to()`, `email.set_subject()`, etc.
  - `client.send(email)` instead of `client.send(email_data)`

**Documentation Updated:**
- `docs/mailersend-adapter.md` - Updated technical implementation section
- `docs/mailersend-adapter.md` - Updated testing examples
- `docs/mailersend-adapter.md` - Added note about official SDK usage

**Files Modified:**
- `backend/server/thirdparty/mailersend.py` - Core adapter implementation
- `docs/mailersend-adapter.md` - Documentation updates

**Impact:**
- MailerSend integration now uses the correct official SDK
- Better error handling and response management
- More reliable email delivery
- Updated documentation reflects actual implementation

---

## Documentation Maintenance Guidelines

When making changes to the backend:

1. **Update relevant adapter documentation** in `docs/` folder
2. **Update API examples** to match actual implementation
3. **Update testing examples** to reflect new API usage
4. **Add changelog entries** for significant changes
5. **Verify documentation accuracy** by testing examples

### Files to Update When Making Changes:

- **SinaliteAdapter changes** → Update `docs/sinalite-adapter.md`
- **MailerSendAdapter changes** → Update `docs/mailersend-adapter.md`
- **SMTPAdapter changes** → Update `docs/smtp-adapter.md`
- **SupabaseAdapter changes** → Update `docs/supabase-adapter.md`
- **Server architecture changes** → Update `docs/server-architecture.md`
- **API endpoint changes** → Update `docs/api-endpoints.md`
