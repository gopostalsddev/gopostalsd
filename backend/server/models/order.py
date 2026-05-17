"""
Order and Payment models for Go Postal SD Application

This module contains models for handling orders, payments, and order items
that result from completed cart checkouts.
"""

from server import database as db
from datetime import datetime
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSON
from enum import Enum


class OrderStatus(Enum):
    """Order status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentStatus(Enum):
    """Payment status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class Order(db.Model):
    """
    Order model for completed purchases.
    This represents a finalized order with payment information.
    """
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), nullable=False, unique=True)  # Human-readable order number
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Optional user association
    session_id = db.Column(db.String(255), nullable=True)  # For guest orders
    
    # Customer information
    customer_email = db.Column(db.String(120), nullable=False)
    customer_first_name = db.Column(db.String(60), nullable=False)
    customer_last_name = db.Column(db.String(60), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=True)
    
    # Order details
    status = db.Column(db.Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    shipping_cost = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    tax_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False, default='USD')
    
    # Shipping information
    shipping_address = db.Column(JSON, nullable=False)  # Full shipping address
    billing_address = db.Column(JSON, nullable=True)  # Billing address (if different)
    
    # Payment information
    payment_status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    payment_provider = db.Column(db.String(50), nullable=True)  # e.g., 'square', 'stripe'
    payment_id = db.Column(db.String(255), nullable=True)  # External payment ID
    payment_method = db.Column(db.String(50), nullable=True)  # e.g., 'card', 'paypal'
    
    # Tracking and fulfillment
    tracking_number = db.Column(db.String(100), nullable=True)
    carrier_name = db.Column(db.String(50), nullable=True)
    estimated_delivery = db.Column(db.DateTime, nullable=True)
    shipped_at = db.Column(db.DateTime, nullable=True)
    delivered_at = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=func.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=func.now(), onupdate=func.now())
    
    # Relationships
    items = db.relationship('OrderItem', back_populates='order', cascade='all, delete-orphan')
    user = db.relationship('User', backref='orders')
    
    def to_dict(self):
        """Convert order to dictionary"""
        return {
            'id': self.id,
            'order_number': self.order_number,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'customer_email': self.customer_email,
            'customer_first_name': self.customer_first_name,
            'customer_last_name': self.customer_last_name,
            'customer_phone': self.customer_phone,
            'status': self.status.value if self.status else None,
            'subtotal': float(self.subtotal),
            'shipping_cost': float(self.shipping_cost),
            'tax_amount': float(self.tax_amount),
            'total_amount': float(self.total_amount),
            'currency': self.currency,
            'shipping_address': self.shipping_address,
            'billing_address': self.billing_address,
            'payment_status': self.payment_status.value if self.payment_status else None,
            'payment_provider': self.payment_provider,
            'payment_id': self.payment_id,
            'payment_method': self.payment_method,
            'tracking_number': self.tracking_number,
            'carrier_name': self.carrier_name,
            'estimated_delivery': self.estimated_delivery.isoformat() if self.estimated_delivery else None,
            'shipped_at': self.shipped_at.isoformat() if self.shipped_at else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
            'items': [item.to_dict() for item in self.items],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class OrderItem(db.Model):
    """
    Individual items in an order.
    This stores the product configuration at the time of purchase.
    """
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)  # Sinalite product ID
    product_name = db.Column(db.String(255), nullable=False)
    product_sku = db.Column(db.String(255), nullable=True)
    quantity = db.Column(db.Integer, nullable=False)
    selected_options = db.Column(JSON, nullable=False)  # Selected option IDs
    option_key = db.Column(db.String(500), nullable=False)  # Combination key for pricing
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    package_info = db.Column(JSON, nullable=True)  # Package details
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=func.now())
    
    # Relationships
    order = db.relationship('Order', back_populates='items')
    
    def to_dict(self):
        """Convert order item to dictionary"""
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'product_sku': self.product_sku,
            'quantity': self.quantity,
            'selected_options': self.selected_options,
            'option_key': self.option_key,
            'unit_price': float(self.unit_price),
            'total_price': float(self.total_price),
            'package_info': self.package_info,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Payment(db.Model):
    """
    Payment model for tracking payment transactions.
    This stores detailed payment information from payment providers.
    """
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    payment_provider = db.Column(db.String(50), nullable=False)  # e.g., 'square', 'stripe'
    external_payment_id = db.Column(db.String(255), nullable=False)  # Provider's payment ID
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False, default='USD')
    status = db.Column(db.Enum(PaymentStatus), nullable=False)
    
    # Payment method details
    payment_method = db.Column(db.String(50), nullable=True)  # e.g., 'card', 'paypal'
    card_last_four = db.Column(db.String(4), nullable=True)
    card_brand = db.Column(db.String(20), nullable=True)  # e.g., 'visa', 'mastercard'
    
    # Provider response data
    provider_response = db.Column(JSON, nullable=True)  # Full provider response
    failure_reason = db.Column(db.String(500), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=func.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=func.now(), onupdate=func.now())
    
    # Relationships
    order = db.relationship('Order', backref='payments')
    
    def to_dict(self):
        """Convert payment to dictionary"""
        return {
            'id': self.id,
            'order_id': self.order_id,
            'payment_provider': self.payment_provider,
            'external_payment_id': self.external_payment_id,
            'amount': float(self.amount),
            'currency': self.currency,
            'status': self.status.value if self.status else None,
            'payment_method': self.payment_method,
            'card_last_four': self.card_last_four,
            'card_brand': self.card_brand,
            'provider_response': self.provider_response,
            'failure_reason': self.failure_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Refund(db.Model):
    """
    Refund model for tracking refund transactions.
    This stores refund information for completed orders.
    """
    __tablename__ = 'refunds'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'), nullable=False)
    refund_amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False, default='USD')
    reason = db.Column(db.String(500), nullable=True)
    
    # Provider refund details
    external_refund_id = db.Column(db.String(255), nullable=True)  # Provider's refund ID
    provider_response = db.Column(JSON, nullable=True)  # Full provider response
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=func.now())
    processed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    order = db.relationship('Order', backref='refunds')
    payment = db.relationship('Payment', backref='refunds')
    
    def to_dict(self):
        """Convert refund to dictionary"""
        return {
            'id': self.id,
            'order_id': self.order_id,
            'payment_id': self.payment_id,
            'refund_amount': float(self.refund_amount),
            'currency': self.currency,
            'reason': self.reason,
            'external_refund_id': self.external_refund_id,
            'provider_response': self.provider_response,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None
        }
