# SinaliteAdapter Documentation

## Overview

The `SinaliteAdapter` is a third-party integration adapter that provides access to the Sinalite API for product catalog management, pricing, and shipping calculations. Sinalite is a print and shipping service provider that offers various postal and shipping products.

## Configuration

### Environment Variables

```bash
# Required - Sinalite API Configuration
SINALITE_BASE_URL=https://apiconnect.sinalite.com
SINALITE_BASE_URL_DEV=https://dev-apiconnect.sinalite.com  # For development
SINALITE_CLIENT_ID=your_client_id
SINALITE_CLIENT_SECRET=your_client_secret
```

### Flask App Configuration

```python
app.config.update({
    'SINALITE_BASE_URL': 'https://apiconnect.sinalite.com',
    'SINALITE_CLIENT_ID': 'your_client_id',
    'SINALITE_CLIENT_SECRET': 'your_client_secret'
})
```

## Authentication

The SinaliteAdapter uses OAuth2 client credentials flow for authentication:

- **Grant Type**: `client_credentials`
- **Audience**: `https://apiconnect.sinalite.com`
- **Token Lifetime**: 1 hour (3600 seconds)
- **Auto-renewal**: Tokens are automatically refreshed when expired

### Authentication Flow

```python
sinalite_adapter = SinaliteAdapter()
sinalite_adapter.init_app(app)

# Authenticate and get access token
if sinalite_adapter.authenticate():
    print("Authentication successful")
else:
    print("Authentication failed")
```

## Core Functionality

### 1. Product Management

#### Get All Products
```python
products = sinalite_adapter.get_products()
# Returns: List of all available products
```

#### Get Product Categories
```python
categories = sinalite_adapter.get_product_categories()
# Returns: Sorted list of unique product categories
```

#### Get Product Details
```python
product_details = sinalite_adapter.get_product_details(
    product_id=123,
    store_code=9  # 6 for Canada, 9 for US
)
# Returns: Detailed product information with options and pricing data
```

**Product Details Response Structure:**
- Product metadata (name, description, category)
- Available options (size, color, material, etc.)
- Pricing combinations
- Package specifications

### 2. Pricing Integration

#### Get Product Price
```python
price_info = sinalite_adapter.get_product_price(
    product_id=123,
    store_code=9,
    product_options=[1, 2, 3]  # List of option IDs
)
# Returns: Price and package information for specific configuration
```

#### Get Product Variants
```python
variants = sinalite_adapter.get_product_variants(
    product_id=123,
    offset=0  # For pagination
)
# Returns: List of variants with prices and keys
```

#### Get Price by Key
```python
price = sinalite_adapter.get_price_by_key(
    product_id=123,
    key="variant_key_string"
)
# Returns: Price information for specific variant
```

### 3. Shipping Integration

#### Get Shipping Estimates
```python
shipping_options = sinalite_adapter.get_shipping_estimate(
    items=[
        {
            "productId": 123,
            "options": [1, 2, 3],
            "quantity": 1
        }
    ],
    shipping_info={
        "country": "US",
        "state": "CA",
        "city": "San Diego",
        "postalCode": "92101",
        "address": "123 Main St"
    }
)
# Returns: Available shipping options with prices and delivery times
```

**Shipping Info Structure:**
- `country`: Country code (US, CA, etc.)
- `state`: State/province code
- `city`: City name
- `postalCode`: ZIP/postal code
- `address`: Street address

## Store Codes

Sinalite uses different store codes for different regions:

- **6**: Canada
- **9**: United States

## Error Handling

The adapter includes comprehensive error handling:

- **Authentication failures**: Logged and returns `False`
- **API errors**: Logged with detailed error messages
- **Network issues**: Handled by the `make_http_request` helper
- **Token expiration**: Automatic renewal on next request

## Usage Examples

### Complete Product Workflow

```python
# Initialize adapter
sinalite_adapter = SinaliteAdapter()
sinalite_adapter.init_app(app)

# Authenticate
if not sinalite_adapter.authenticate():
    raise Exception("Failed to authenticate with Sinalite")

# Get product catalog
products = sinalite_adapter.get_products()
categories = sinalite_adapter.get_product_categories()

# Get specific product details
product_id = 123
product_details = sinalite_adapter.get_product_details(product_id, store_code=9)

# Calculate pricing for specific configuration
price_info = sinalite_adapter.get_product_price(
    product_id=product_id,
    store_code=9,
    product_options=[1, 2, 3]
)

# Get shipping estimate
shipping_options = sinalite_adapter.get_shipping_estimate(
    items=[{
        "productId": product_id,
        "options": [1, 2, 3],
        "quantity": 1
    }],
    shipping_info={
        "country": "US",
        "state": "CA",
        "city": "San Diego",
        "postalCode": "92101"
    }
)
```

### Integration with Cart System

```python
def calculate_cart_total(cart_items, shipping_address):
    """Calculate total cost including products and shipping."""
    
    # Calculate product costs
    total_product_cost = 0
    items_for_shipping = []
    
    for item in cart_items:
        price_info = sinalite_adapter.get_product_price(
            product_id=item['product_id'],
            store_code=9,
            product_options=item['options']
        )
        
        if price_info:
            total_product_cost += price_info['price'] * item['quantity']
            items_for_shipping.append({
                "productId": item['product_id'],
                "options": item['options'],
                "quantity": item['quantity']
            })
    
    # Calculate shipping
    shipping_options = sinalite_adapter.get_shipping_estimate(
        items=items_for_shipping,
        shipping_info=shipping_address
    )
    
    # Select cheapest shipping option
    cheapest_shipping = min(shipping_options, key=lambda x: x['price'])
    
    return {
        'product_total': total_product_cost,
        'shipping_cost': cheapest_shipping['price'],
        'total_cost': total_product_cost + cheapest_shipping['price'],
        'shipping_options': shipping_options
    }
```

## Logging and Monitoring

The adapter provides detailed logging for:

- Authentication status
- API request/response details
- Error conditions
- Performance metrics

### Debug Logging

```python
import logging
logging.getLogger('server.thirdparty.sinalite').setLevel(logging.DEBUG)
```

## Best Practices

1. **Token Management**: Always check `is_access_expired()` before making requests
2. **Error Handling**: Always handle potential `None` returns from API calls
3. **Caching**: Consider caching product data to reduce API calls
4. **Rate Limiting**: Be mindful of API rate limits for high-volume operations
5. **Store Code**: Always use the correct store code (6 for CA, 9 for US)

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Verify `SINALITE_CLIENT_ID` and `SINALITE_CLIENT_SECRET`
   - Check network connectivity to Sinalite API
   - Verify API credentials are active

2. **Product Not Found**
   - Verify product ID exists in Sinalite catalog
   - Check if product is available for specified store code
   - Ensure product is not discontinued

3. **Pricing Errors**
   - Verify product options are valid
   - Check if options combination is available
   - Ensure store code matches product availability

4. **Shipping Calculation Failed**
   - Verify shipping address format
   - Check if destination is supported
   - Ensure cart items are valid

## API Rate Limits

Sinalite API has rate limits that should be respected:

- **Authentication**: Limited requests per minute
- **Product queries**: Moderate rate limits
- **Pricing calculations**: Higher rate limits
- **Shipping estimates**: Lower rate limits (more expensive operation)

## Security Considerations

- **Credentials**: Store API credentials securely in environment variables
- **Token Security**: Access tokens are stored in memory only
- **HTTPS**: All API communication uses HTTPS
- **Logging**: Avoid logging sensitive data (credentials, tokens)

## Future Enhancements

Potential improvements for the SinaliteAdapter:

1. **Caching Layer**: Implement Redis caching for product data
2. **Batch Operations**: Support for bulk pricing calculations
3. **Webhook Support**: Real-time updates for product changes
4. **Analytics**: Track API usage and performance metrics
5. **Retry Logic**: Implement exponential backoff for failed requests
