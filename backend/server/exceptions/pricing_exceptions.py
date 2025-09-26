"""
Custom exceptions for pricing operations.
Provides specific error types for better error handling.
"""


class PricingError(Exception):
    """Base exception for pricing-related errors."""
    pass


class ProductNotFoundError(PricingError):
    """Raised when a product is not found."""
    def __init__(self, product_id: int):
        self.product_id = product_id
        super().__init__(f"Product {product_id} not found")


class PricingCalculationError(PricingError):
    """Raised when price calculation fails."""
    def __init__(self, product_id: int, reason: str = None):
        self.product_id = product_id
        self.reason = reason
        message = f"Failed to calculate price for product {product_id}"
        if reason:
            message += f": {reason}"
        super().__init__(message)


class CartNotFoundError(PricingError):
    """Raised when a cart is not found."""
    def __init__(self, cart_id: int):
        self.cart_id = cart_id
        super().__init__(f"Cart {cart_id} not found")


class CartItemNotFoundError(PricingError):
    """Raised when a cart item is not found."""
    def __init__(self, cart_item_id: int):
        self.cart_item_id = cart_item_id
        super().__init__(f"Cart item {cart_item_id} not found")


class InvalidOptionsError(PricingError):
    """Raised when invalid options are provided."""
    def __init__(self, options: list, reason: str = None):
        self.options = options
        self.reason = reason
        message = f"Invalid options provided: {options}"
        if reason:
            message += f" - {reason}"
        super().__init__(message)


class ShippingEstimateError(PricingError):
    """Raised when shipping estimate fails."""
    def __init__(self, reason: str = None):
        self.reason = reason
        message = "Failed to get shipping estimate"
        if reason:
            message += f": {reason}"
        super().__init__(message)
