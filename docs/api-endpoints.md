# Go Postal SD API Endpoints

## Overview

The Go Postal SD API provides RESTful endpoints for managing postal services, product catalog, pricing, shopping cart, user authentication, and contact forms. All endpoints follow RESTful conventions and include comprehensive Swagger documentation.

## Base URL

```
Development: http://localhost:5000/api
Production: https://api.gopostalsd.com/api
```

## Authentication

Most endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <jwt_token>
```

## API Namespaces

- **`/api/auth`** - Authentication and user management
- **`/api/pricing`** - Product pricing and shipping calculations
- **`/api/cart`** - Shopping cart operations
- **`/api/print`** - Print product catalog
- **`/api/contact`** - Contact form submissions

---

## Authentication Endpoints (`/api/auth`)

### POST `/api/auth/register`
**Description:** Register a new user account

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "secure_password",
  "first_name": "John",
  "last_name": "Doe",
  "shipping_address": {
    "street": "123 Main St",
    "city": "San Diego",
    "state": "CA",
    "zip_code": "92101",
    "country": "US",
    "apt": "Apt 1"
  },
  "billing_address": {
    "street": "123 Main St",
    "city": "San Diego",
    "state": "CA",
    "zip_code": "92101",
    "country": "US"
  }
}
```

**Response:**
```json
{
  "user_id": 123,
  "email": "user@example.com",
  "message": "Registration successful",
  "verification_required": true
}
```

### POST `/api/auth/login`
**Description:** Authenticate user and create session

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "user": {
    "id": 123,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "user",
    "email_verified": true,
    "status": "active"
  },
  "session": {
    "session_token": "jwt_token_here",
    "refresh_token": "refresh_token_here",
    "expires_at": "2024-01-01T12:00:00Z"
  }
}
```

### POST `/api/auth/logout`
**Description:** Logout user and invalidate session

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "message": "Logout successful"
}
```

### POST `/api/auth/verify-email`
**Description:** Verify user email address

**Request Body:**
```json
{
  "token": "verification_token"
}
```

**Response:**
```json
{
  "message": "Email verified successfully"
}
```

### POST `/api/auth/resend-verification`
**Description:** Resend email verification

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "message": "Verification email sent"
}
```

### POST `/api/auth/forgot-password`
**Description:** Request password reset

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "message": "Password reset email sent"
}
```

### POST `/api/auth/reset-password`
**Description:** Reset password with token

**Request Body:**
```json
{
  "token": "reset_token",
  "new_password": "new_secure_password"
}
```

**Response:**
```json
{
  "message": "Password reset successful"
}
```

### POST `/api/auth/validate-password`
**Description:** Validate password strength

**Request Body:**
```json
{
  "password": "password_to_validate"
}
```

**Response:**
```json
{
  "is_valid": true,
  "errors": [],
  "warnings": [],
  "strength_score": 85,
  "strength_level": "strong"
}
```

### GET `/api/auth/profile`
**Description:** Get current user profile

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "id": 123,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "user",
  "email_verified": true,
  "status": "active",
  "created_at": "2024-01-01T00:00:00Z",
  "last_login": "2024-01-01T12:00:00Z"
}
```

### PUT `/api/auth/profile`
**Description:** Update user profile

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "shipping_address": {
    "street": "123 Main St",
    "city": "San Diego",
    "state": "CA",
    "zip_code": "92101",
    "country": "US"
  }
}
```

**Response:**
```json
{
  "message": "Profile updated successfully"
}
```

---

## Pricing Endpoints (`/api/pricing`)

### GET `/api/pricing/products/{product_id}/options`
**Description:** Get available options for a product

**Parameters:**
- `product_id` (path): Product ID
- `store_code` (query): Store code (6 for Canada, 9 for US, default: 6)

**Response:**
```json
[
  {
    "group": "Size",
    "options": [
      {
        "id": 1,
        "name": "Small"
      },
      {
        "id": 2,
        "name": "Large"
      }
    ]
  }
]
```

### POST `/api/pricing/products/{product_id}/price`
**Description:** Calculate price for product with selected options

**Parameters:**
- `product_id` (path): Product ID

**Request Body:**
```json
{
  "options": [1, 2, 3],
  "store_code": 6
}
```

**Response:**
```json
{
  "price": 15.99,
  "currency": "CAD",
  "estimated_ship_date": "2024-01-15"
}
```

### POST `/api/pricing/shipping/estimate`
**Description:** Get shipping estimates for cart items

**Request Body:**
```json
{
  "items": [
    {
      "productId": 123,
      "options": [1, 2]
    }
  ],
  "shippingInfo": {
    "ShipState": "CA",
    "ShipZip": "92101",
    "ShipCountry": "US"
  }
}
```

**Response:**
```json
[
  {
    "carrier_name": "Canada Post",
    "method_name": "Standard",
    "price": 8.99,
    "shipping_days": 3
  },
  {
    "carrier_name": "Canada Post",
    "method_name": "Express",
    "price": 15.99,
    "shipping_days": 1
  }
]
```

### GET `/api/pricing/cart/{cart_id}/totals`
**Description:** Calculate cart totals including tax and shipping

**Parameters:**
- `cart_id` (path): Cart ID

**Response:**
```json
{
  "subtotal": 45.99,
  "tax": 5.99,
  "total": 51.98,
  "item_count": 3
}
```

---

## Cart Endpoints (`/api/cart`)

### GET `/api/cart/`
**Description:** Get or create a cart

**Parameters:**
- `session_id` (query): Required session identifier for the client cart
- `user_id` (query): User ID (optional)
- `store_code` (query): Store code (default: 6)

**Response:**
```json
{
  "cart_id": 123,
  "session_id": "session_123",
  "user_id": 456,
  "store_code": 6,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

### POST `/api/cart/{cart_id}/items`
**Description:** Add item to cart

**Parameters:**
- `cart_id` (path): Cart ID

**Request Body:**
```json
{
  "product_id": 123,
  "product_name": "Custom Postcard",
  "product_sku": "PC-001",
  "selected_options": [1, 2, 3],
  "quantity": 1
}
```

**Response:**
```json
{
  "cart_item_id": 789,
  "cart_id": 123,
  "product_id": 123,
  "product_name": "Custom Postcard",
  "product_sku": "PC-001",
  "selected_options": [1, 2, 3],
  "quantity": 1,
  "unit_price": 15.99,
  "total_price": 15.99,
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

### GET `/api/cart/{cart_id}/items`
**Description:** Get all items in cart

**Parameters:**
- `cart_id` (path): Cart ID

**Response:**
```json
[
  {
    "cart_item_id": 789,
    "cart_id": 123,
    "product_id": 123,
    "product_name": "Custom Postcard",
    "product_sku": "PC-001",
    "selected_options": [1, 2, 3],
    "quantity": 1,
    "unit_price": 15.99,
    "total_price": 15.99
  }
]
```

### PUT `/api/cart/{cart_id}/items/{item_id}`
**Description:** Update cart item quantity

**Parameters:**
- `cart_id` (path): Cart ID
- `item_id` (path): Cart item ID

**Request Body:**
```json
{
  "quantity": 2
}
```

**Response:**
```json
{
  "message": "Item updated successfully"
}
```

### DELETE `/api/cart/{cart_id}/items/{item_id}`
**Description:** Remove item from cart

**Parameters:**
- `cart_id` (path): Cart ID
- `item_id` (path): Cart item ID

**Response:**
```json
{
  "message": "Item removed successfully"
}
```

### DELETE `/api/cart/{cart_id}/items`
**Description:** Clear all items from cart

**Parameters:**
- `cart_id` (path): Cart ID

**Response:**
```json
{
  "message": "Cart cleared successfully"
}
```

---

## Print Product Endpoints (`/api/print`)

### GET `/api/print/products`
**Description:** Get all available print products

**Response:**
```json
[
  {
    "id": 123,
    "name": "Custom Postcard",
    "sku": "PC-001",
    "category_id": 1,
    "type_id": 1,
    "description": "High-quality custom postcards",
    "image": "https://example.com/image.jpg",
    "vendor_id": 1,
    "vendor_product_id": "VPC-001",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

### GET `/api/print/categories/all`
**Description:** Get all product categories with classification status

**Response:**
```json
[
  {
    "id": 1,
    "name": "Postcards",
    "description": "Custom postcard products",
    "image": "https://example.com/category.jpg",
    "enabled": true,
    "product_classification_status": "classified",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

### GET `/api/print/categories/{category_id}/types`
**Description:** Get product types for a category

**Parameters:**
- `category_id` (path): Category ID

**Response:**
```json
[
  {
    "id": 1,
    "name": "Standard Postcard",
    "category_id": 1,
    "description": "Standard size postcard",
    "image": "https://example.com/type.jpg",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

### GET `/api/print/vendors`
**Description:** Get all vendors

**Response:**
```json
[
  {
    "id": 1,
    "name": "Sinalite",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

---

## Contact Endpoints (`/api/contact`)

### POST `/api/contact/`
**Description:** Submit contact form

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "555-1234",
  "subject": "Inquiry about services",
  "message": "I would like to know more about your postal services."
}
```

**Response:**
```json
{
  "message": "Contact form submitted successfully"
}
```

---

## Error Responses

All endpoints return standardized error responses:

### 400 Bad Request
```json
{
  "error": "Validation error message",
  "details": "Additional error details"
}
```

### 401 Unauthorized
```json
{
  "error": "Authentication required",
  "message": "Please provide a valid token"
}
```

### 403 Forbidden
```json
{
  "error": "Access denied",
  "message": "Insufficient permissions"
}
```

### 404 Not Found
```json
{
  "error": "Resource not found",
  "message": "The requested resource does not exist"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred"
}
```

---

## Rate Limiting

API endpoints are rate-limited to prevent abuse:

- **Authentication endpoints**: 5 requests per minute per IP
- **General endpoints**: 100 requests per minute per IP
- **Pricing endpoints**: 50 requests per minute per IP

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

---

## API Documentation

Interactive API documentation is available at:
- **Swagger UI (local)**: `http://localhost:5000/`
- **Swagger UI (deployed)**: `<backend-base-url>/`

The API documentation includes:
- Complete endpoint descriptions
- Request/response schemas
- Authentication requirements
- Example requests and responses
- Error code documentation
