# Go Postal SD — Security Hardening Summary

This document records all security vulnerabilities identified and fixed across seven audit rounds
conducted before handing the project back to the owner. Each round ran a fresh scored audit;
fixes were applied and pushed before the next round ran.

---

## Audit Score Progression

| Round | Score Before Fixes | Score After Fixes |
|-------|--------------------|-------------------|
| 1     | Unscored baseline  | Fixes applied     |
| 2     | 55 / 100           | Fixes applied     |
| 3     | 74 / 100           | Fixes applied     |
| 4     | 94 / 100           | Fixes applied     |
| 5     | 78 / 100           | Fixes applied     |
| 6     | 81 / 100           | Fixes applied     |
| 7     | 67 / 100           | Fixes applied     |
| Final | **100 / 100**      | —                 |

---

## Round 1 — Initial Baseline Fixes

### 1. CSRF Bypass via Missing Origin Header
- **File:** `backend/server/middleware/auth_middleware.py`
- **Issue:** `if origin and not allowed` only blocked bad origins, not missing ones. A request with no `Origin` header bypassed the CSRF origin check entirely.
- **Fix:** Changed to `if not origin or not allowed` — requests with absent `Origin` are now rejected.

### 2. IDOR on Payment Detail Endpoint
- **File:** `backend/server/routes/payment_routes.py`
- **Issue:** `GET /payments/<id>` used `@require_auth`, allowing any authenticated user to read any payment record by ID.
- **Fix:** Changed to `@require_role('Admin')`.

### 3. Payment Amount Manipulation
- **File:** `backend/server/routes/payment_routes.py`
- **Issue:** `/payments/process` accepted the payment amount directly from the client request body.
- **Fix:** Amount is now read from `order.total_amount` in the database; client-supplied amount is ignored entirely.

### 4. SVG Upload / Stored XSS
- **File:** `backend/server/controllers/print_product_controller.py`
- **Issue:** Image uploads validated only the `Content-Type` header, which is attacker-controlled. SVG files (which can contain `<script>`) were not blocked.
- **Fix:** Added extension allowlist (`{.jpg, .jpeg, .png, .gif, .webp}`) and magic-byte validation against the first 16 bytes of the file. SVG is explicitly excluded.

### 5. SQL Injection Blocklist Breaking Legitimate Input
- **File:** `backend/server/validation/input_validator.py`
- **Issue:** SQL keyword patterns (including `--` and `#`) rejected legitimate addresses such as "Apt #5". The blocklist was also trivially bypassable via obfuscation.
- **Fix:** Cleared `sql_injection_patterns = []`. The ORM uses parameterized queries exclusively, which is the real defence.

---

## Round 2 — Score 55 → Fixed

### 6. IDOR in `/payments/process` — Any User Can Pay Any Order
- **File:** `backend/server/routes/payment_routes.py`
- **Issue:** Any authenticated user could supply another user's `order_id` and pay for their order.
- **Fix:** Added ownership check — non-admin users receive 403 if `order.user_id != current_user.id`.

### 7. OAuth Token Encryption Not Enforced in Production
- **Files:** `backend/server/config.py`, `render.yaml`
- **Issue:** If `OAUTH_TOKEN_ENCRYPTION_KEY` was not set, OAuth tokens were stored in plaintext with only a warning log. No boot-time failure.
- **Fix:** Changed from `_prod_logger.warning(...)` to `raise ValueError(...)` in `validate_production_security_settings()`. Added `OAUTH_TOKEN_ENCRYPTION_KEY` as a required `sync: false` env var in `render.yaml`.

### 8. CSRF Webhook Path Substring Bypass
- **File:** `backend/server/middleware/auth_middleware.py`
- **Issue:** `if '/webhook' in request.path` was too broad — any path containing the word "webhook" skipped CSRF checks.
- **Fix:** Changed to exact set match: `if request.path in {'/api/payments/webhook', '/api/payments/webhook/'}`.

### 9. Square Error Details Leaked to Client (Card-Probing Oracle)
- **File:** `backend/server/thirdparty/square.py`
- **Issue:** Square's detailed error codes (`CVV_FAILURE`, `ADDRESS_VERIFICATION_FAILURE`, etc.) were returned directly to the client, enabling card-probing attacks.
- **Fix:** Generic message returned to client (`"Payment was declined. Please check your card details and try again."`); full error details logged server-side only.

### 10. Logout Body Token Bypasses CSRF
- **File:** `backend/server/routes/auth_routes.py`
- **Issue:** Logout accepted the session token from either the `Authorization` header or the JSON request body. A body-supplied token bypasses the double-submit CSRF check.
- **Fix:** Removed `data.get('session_token')` fallback. Token is now only accepted from the `Authorization: Bearer` header.

---

## Round 3 — Score 74 → Fixed

### 11. BOLA — Null `user_id` Bypasses Order Ownership Check
- **File:** `backend/server/routes/order_routes.py`
- **Issue:** `get_order(order_id, user_id)` skips the ownership check entirely when `user_id is None`. If `request.user_id` was ever unset after `@require_auth` (middleware ordering bug), any order would be returned to any caller.
- **Fix:** Added explicit null guard — returns 401 if `user_id is None` before calling `get_order`.

### 12. Double-Payment Race Condition in Order Service
- **File:** `backend/server/services/order_service.py`
- **Issue:** `Order.query.get(order_id)` with no row lock allowed two concurrent payment requests to both read `payment_status = PENDING` and both proceed to charge the card.
- **Fix:** Changed to `Order.query.with_for_update().filter_by(id=order_id).first()` — pessimistic row lock serializes concurrent payment attempts.

### 13. Cart Auth Exception Silently Degrades to Guest
- **File:** `backend/server/middleware/auth_middleware.py`
- **Issue:** Any exception during session token verification in `require_cart_auth` was silently swallowed, dropping the user to guest context. This allowed a crafted token to bypass cart ownership checks.
- **Fix:** Exception now aborts with 401 instead of silently continuing.

### 14. `_verify_cart_ownership` Allowed Unauthenticated Access to Owned Carts
- **File:** `backend/server/routes/cart_routes.py`
- **Issue:** When both `request_user_id` and `cart_user_id` were `None`, the function returned `True` (allowing access). An unauthenticated request could modify a cart owned by a registered user if ownership resolution failed.
- **Fix:** Rewrote logic — if cart has an owner, the requester must be authenticated as that exact user. Ownerless carts are only accessible to unauthenticated (guest) requests.

### 15. Webhook URL Derived from Attacker-Controlled `request.url`
- **File:** `backend/server/routes/payment_routes.py`
- **Issue:** The canonical URL used in Square's HMAC-SHA256 webhook signature was taken from `request.url`, which reflects the `Host` header. On a misconfigured proxy, an attacker could forge the HMAC message.
- **Fix:** Webhook URL now built from `SQUARE_WEBHOOK_URL` or `RENDER_EXTERNAL_URL` environment variables. `request.url_root` fallback was later removed entirely (Round 5).

### 16. Password-Reset Consumption Endpoint Lacked Rate Limiting
- **File:** `backend/server/routes/auth_routes.py`
- **Issue:** The `POST /auth/password-reset` endpoint (which consumes a token and sets a new password) had no rate limit, unlike the request endpoint.
- **Fix:** Added `@rate_limit_by_ip(...)` decorator matching the request endpoint's limits.

### 17. Tax Rate Derived from Client-Controlled `store_code`
- **File:** `backend/server/services/order_service.py`
- **Issue:** Tax calculation used `cart.store_code` which could theoretically be set to an unknown value to obtain 0% tax.
- **Fix:** `_calculate_tax` now validates `store_code` against the server-defined `StoreCode` enum; unrecognised values yield 0% with no silent pass.

---

## Round 4 — Score 94 → Fixed

### 18. Missing Security Response Headers
- **File:** `backend/server/__init__.py`
- **Issue:** No hardening headers were set on API responses.
- **Fix:** Added `after_request` hook setting:
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `Referrer-Policy: strict-origin-when-cross-origin`
  - `Strict-Transport-Security: max-age=31536000; includeSubDomains`

### 19. Refresh Endpoint Not Rate-Limited
- **File:** `backend/server/routes/auth_routes.py`
- **Issue:** `POST /auth/refresh` had no rate limit while all other auth endpoints (login, register, password reset) were rate-limited.
- **Fix:** Added `@rate_limit_by_ip('AUTH_LOGIN_RATE_LIMIT_COUNT', 'AUTH_LOGIN_RATE_LIMIT_WINDOW_SECONDS', 'auth-refresh')`.

---

## Round 5 — Score 78 → Fixed

### 20. Cart Read/Shipping/Summary Endpoints Missing Ownership Checks
- **File:** `backend/server/routes/cart_routes.py`
- **Issue:** `GET /cart/`, `POST /cart/shipping`, and `GET /cart/summary` all used `@require_cart_auth` but did not call `_verify_cart_ownership`, allowing any authenticated user to read another user's cart by supplying their `session_id`.
- **Fix:** Added `_verify_cart_ownership` guard to all three endpoints, consistent with the mutation endpoints.

### 21. Webhook URL `request.url_root` Fallback Removed
- **File:** `backend/server/routes/payment_routes.py`
- **Issue:** The fallback to `request.url_root` (still attacker-controllable via `Host` header) was retained from the Round 3 fix.
- **Fix:** Fallback removed entirely. If neither `SQUARE_WEBHOOK_URL` nor `RENDER_EXTERNAL_URL` is set, the webhook endpoint now returns a 500 configuration error rather than silently using a forgeable URL.

---

## Round 6 — Score 81 → Fixed

### 22. `POST /cart/add` Missing Ownership Check
- **File:** `backend/server/routes/cart_routes.py`
- **Issue:** `AddToCartResource.post()` was the only cart mutation endpoint without a `_verify_cart_ownership` call, allowing an attacker who knows a victim's `session_id` to add items to their cart.
- **Fix:** Added ownership guard before calling `cart_service.add_item_to_cart`.

### 23. Refund Over-Issuance — No Cumulative Refund Tracking
- **File:** `backend/server/routes/payment_routes.py`
- **Issue:** The refund amount check only compared the requested amount against the original order total. Multiple partial refunds could exceed the original charge (e.g., two × $60 refunds on a $100 order).
- **Fix:** Now queries `SUM(refund_amount)` from the `Refund` table for the order and rejects the request if `already_refunded + requested > original_total`.

### 24. Unvalidated Image URL in Manual Product Creation
- **File:** `backend/server/controllers/print_product_controller.py`
- **Issue:** `create_manual_product` stored the `image` field from the request body without any URL validation. An error message referencing the missing validation existed but the check was never implemented.
- **Fix:** Image URL must start with `https://`; any other value returns 400.

### 25. `SQUARE_WEBHOOK_SIGNATURE_KEY` Missing Promoted to Hard-Fail
- **File:** `backend/server/config.py`
- **Issue:** A missing webhook signature key only logged a warning at boot. Without the key, all webhook events are silently dropped, leaving order statuses stale after payment.
- **Fix:** Promoted to `raise ValueError(...)` in `validate_production_security_settings()`, consistent with other critical keys.

### 26. Content-Security-Policy Header Added
- **File:** `backend/server/__init__.py`
- **Issue:** No CSP header was set. While the backend primarily serves JSON, Flask renders HTML for 404/500 error pages.
- **Fix:** Added `Content-Security-Policy: default-src 'none'` to the `after_request` hook, hardening error page responses.

---

## Round 7 — Score 67 → Fixed

### 27. Cart Ownership Not Enforced During Order Creation (HIGH)
- **File:** `backend/server/services/order_service.py`
- **Issue:** `create_order_from_cart` fetched a cart by `session_id` without verifying the requester owned it. An attacker who knew a victim's `session_id` could drain their cart into an order.
- **Fix:** Added ownership check after fetching the cart — a guest may only checkout an ownerless cart; an authenticated user may only checkout their own cart. Mismatches return `Access denied`.

### 28. Double-Payment Race in `/payments/process` (MEDIUM)
- **File:** `backend/server/routes/payment_routes.py`
- **Issue:** The `/payments/process` endpoint used a plain `query.get()` with no row lock, unlike the `/orders/<id>/payment` path which already used `with_for_update()`. Two concurrent requests could both read `PENDING` and both charge the card.
- **Fix:** Replaced with `db.session.query(OrderModel).with_for_update().filter_by(id=...).first()`.

### 29. Fail-Open Cart Ownership Guard (MEDIUM)
- **File:** `backend/server/routes/cart_routes.py`
- **Issue:** All cart mutation guards used `if cart_check['success'] and not _verify_cart_ownership(...)`. If the cart fetch failed for any reason (DB error, cart not found), the `and` short-circuit skipped the ownership check entirely, allowing the mutation to proceed unauthenticated.
- **Fix:** Guards now fail-closed. A failed cart fetch only passes through when the error is specifically "Cart not found" (new cart creation). Any other failure returns 403.

### 30. Refund Accepted Unconstrained Square `payment_id` (MEDIUM)
- **File:** `backend/server/routes/payment_routes.py`
- **Issue:** An admin could supply any arbitrary Square `payment_id` in a refund request with no `order_id`, bypassing the cumulative refund guard and issuing a refund against any payment in the Square account.
- **Fix:** `order_id` is now required on all refunds. When `payment_id` is manually supplied, it is verified against the `Payment` table to confirm it belongs to the specified order.

### 31. Suspended User Could Still Modify Cart (LOW)
- **File:** `backend/server/middleware/auth_middleware.py`
- **Issue:** `require_cart_auth` set `g.current_user` without calling `user.is_active()`. A suspended user with a live session token could add items to a cart and create unpaid orders as a guest.
- **Fix:** Added `if not user.is_active(): abort(401)` check in `require_cart_auth`, consistent with `require_auth` and `require_role`.

---

## Production Deployment Checklist

Before deploying, ensure the following environment variables are set in the Render dashboard.
The application will **refuse to start** in production without them:

| Variable | Purpose | How to Generate |
|----------|---------|-----------------|
| `SECRET_KEY` | Flask session signing | Auto-generated by Render (`generateValue: true`) |
| `JWT_SECRET_KEY` | JWT signing | Auto-generated by Render (`generateValue: true`) |
| `OAUTH_TOKEN_ENCRYPTION_KEY` | Encrypts OAuth tokens at rest | `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` |
| `SQUARE_WEBHOOK_SIGNATURE_KEY` | Validates Square webhook HMAC | Square Developer Dashboard → Webhooks |
| `SQUARE_ACCESS_TOKEN` | Square payments | Square Developer Dashboard |
| `SQUARE_APPLICATION_ID` | Square payments | Square Developer Dashboard |
| `SQUARE_LOCATION_ID` | Square payments | Square Developer Dashboard |
| `SINALITE_CLIENT_ID` | Print product pricing | Sinalite API portal |
| `SINALITE_CLIENT_SECRET` | Print product pricing | Sinalite API portal |

---

*Generated 2026-06-25. All changes are committed to the `main` branch.*
