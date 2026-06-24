"""
Pricing and cart related models for the Go Postal SD application.

This module contains models for handling product pricing, cart functionality,
and shipping information using the Sinalite API integration.
"""

from server import database as db
from datetime import datetime
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSON
from enum import Enum


class StoreCode(Enum):
    """Store codes for different regions"""
    CANADA = 6
    US = 9


class ProductOption(db.Model):
    """
    Model for storing product options from Sinalite API.
    This caches option data to reduce API calls and improve performance.
    """
    __tablename__ = 'product_options'
    __table_args__ = (
        db.UniqueConstraint('product_id', 'sinalite_option_id', name='uq_product_options_product_option'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    sinalite_option_id = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, nullable=False)  # Sinalite product ID
    group = db.Column(db.String(100), nullable=False)  # e.g., 'qty', 'size', 'Stock'
    name = db.Column(db.String(255), nullable=False)  # e.g., '50', '9 x 12 x 9'
    created_at = db.Column(db.DateTime, nullable=False, default=func.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        """Convert product option to dictionary"""
        return {
            'id': self.sinalite_option_id,
            'group': self.group,
            'name': self.name,
            'product_id': self.product_id
        }


class ProductPricing(db.Model):
    """
    Model for caching product pricing information from Sinalite API.
    This helps reduce API calls and improve response times.
    """
    __tablename__ = 'product_pricing'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, nullable=False)  # Sinalite product ID
    store_code = db.Column(db.Integer, nullable=False)  # Store code (6 for Canada, 9 for US)
    option_key = db.Column(db.String(500), nullable=False)  # Combination of option IDs
    price = db.Column(db.Numeric(10, 2), nullable=False)
    package_info = db.Column(JSON, nullable=True)  # Package details from API
    product_options = db.Column(JSON, nullable=True)  # Selected options
    created_at = db.Column(db.DateTime, nullable=False, default=func.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=func.now(), onupdate=func.now())
    
    # Composite unique constraint
    __table_args__ = (db.UniqueConstraint('product_id', 'store_code', 'option_key', name='unique_pricing'),)
    
    def to_dict(self):
        """Convert product pricing to dictionary"""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'store_code': self.store_code,
            'option_key': self.option_key,
            'price': float(self.price),
            'package_info': self.package_info,
            'product_options': self.product_options,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Cart(db.Model):
    """
    Shopping cart model for storing user cart sessions.
    This can be extended to support persistent carts for logged-in users.
    """
    __tablename__ = 'carts'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(255), nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Optional user association
    store_code = db.Column(db.Integer, nullable=False, default=StoreCode.CANADA.value)
    created_at = db.Column(db.DateTime, nullable=False, default=func.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=func.now(), onupdate=func.now())
    
    # Relationships
    items = db.relationship('CartItem', back_populates='cart', cascade='all, delete-orphan')
    user = db.relationship('User', backref='carts')
    
    def to_dict(self):
        """Convert cart to dictionary"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'store_code': self.store_code,
            'items': [item.to_dict() for item in self.items],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class CartItem(db.Model):
    """
    Individual items in a shopping cart.
    Stores product configuration and quantity.
    """
    __tablename__ = 'cart_items'
    
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)  # Sinalite product ID
    product_name = db.Column(db.String(255), nullable=False)
    product_sku = db.Column(db.String(255), nullable=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    selected_options = db.Column(JSON, nullable=False)  # Selected option IDs
    option_key = db.Column(db.String(500), nullable=False)  # Combination key for pricing
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    package_info = db.Column(JSON, nullable=True)  # Package details
    created_at = db.Column(db.DateTime, nullable=False, default=func.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=func.now(), onupdate=func.now())
    
    # Relationships
    cart = db.relationship('Cart', back_populates='items')
    
    def to_dict(self):
        """Convert cart item to dictionary"""
        # Ensure selected_options is properly serialized
        selected_options = self.selected_options
        if selected_options is None:
            selected_options = []
        elif isinstance(selected_options, str):
            # If it's stored as a string, parse it
            import json
            selected_options = json.loads(selected_options)
        
        return {
            'id': self.id,
            'cart_id': self.cart_id,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'product_sku': self.product_sku,
            'quantity': self.quantity,
            'selected_options': selected_options,
            'option_key': self.option_key,
            'unit_price': float(self.unit_price),
            'total_price': float(self.total_price),
            'package_info': self.package_info,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ShippingOption(db.Model):
    """
    Model for storing shipping options and estimates.
    This caches shipping data to reduce API calls.
    """
    __tablename__ = 'shipping_options'
    
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    carrier_name = db.Column(db.String(100), nullable=False)  # e.g., 'UPS', 'FedEx'
    method_name = db.Column(db.String(100), nullable=False)  # e.g., 'UPS Standard'
    price = db.Column(db.Numeric(10, 2), nullable=False)
    shipping_days = db.Column(db.Integer, nullable=False)
    destination_state = db.Column(db.String(10), nullable=True)  # State/Province code
    destination_zip = db.Column(db.String(20), nullable=True)  # ZIP/Postal code
    destination_country = db.Column(db.String(10), nullable=True)  # Country code
    created_at = db.Column(db.DateTime, nullable=False, default=func.now())
    
    # Relationships
    cart = db.relationship('Cart', backref='shipping_options')
    
    def to_dict(self):
        """Convert shipping option to dictionary"""
        return {
            'id': self.id,
            'cart_id': self.cart_id,
            'carrier_name': self.carrier_name,
            'method_name': self.method_name,
            'price': float(self.price),
            'shipping_days': self.shipping_days,
            'destination_state': self.destination_state,
            'destination_zip': self.destination_zip,
            'destination_country': self.destination_country,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ProductVariant(db.Model):
    """
    Model for caching product variants from Sinalite API.
    This stores the variant key and price combinations.
    """
    __tablename__ = 'product_variants'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, nullable=False)  # Sinalite product ID
    variant_key = db.Column(db.String(500), nullable=False)  # Option combination key
    price = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=func.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=func.now(), onupdate=func.now())
    
    # Composite unique constraint
    __table_args__ = (db.UniqueConstraint('product_id', 'variant_key', name='unique_variant'),)
    
    def to_dict(self):
        """Convert product variant to dictionary"""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'variant_key': self.variant_key,
            'price': float(self.price),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class PricingPolicy(db.Model):
    """Persisted pricing policy settings editable from the admin console."""
    __tablename__ = 'pricing_policies'

    id = db.Column(db.Integer, primary_key=True)
    vendor_currency = db.Column(db.String(8), nullable=False, default='CAD')
    display_currency = db.Column(db.String(8), nullable=False, default='USD')
    cad_to_usd_rate = db.Column(db.Numeric(10, 4), nullable=False, default=0.74)
    exchange_buffer_percent = db.Column(db.Numeric(10, 2), nullable=False, default=5)
    markup_percent = db.Column(db.Numeric(10, 2), nullable=False, default=30)
    fixed_fee_usd = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    minimum_profit_usd = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    rounding_increment = db.Column(db.Numeric(10, 2), nullable=False, default=0.05)
    customization_file_review_fee_usd = db.Column(db.Numeric(10, 2), nullable=False, default=10)
    customization_design_assist_fee_usd = db.Column(db.Numeric(10, 2), nullable=False, default=35)
    created_at = db.Column(db.DateTime, nullable=False, default=func.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=func.now(), onupdate=func.now())

    @classmethod
    def get_current(cls):
        return cls.query.order_by(cls.id.asc()).first()

    def to_dict(self):
        return {
            'id': self.id,
            'vendor_currency': self.vendor_currency,
            'display_currency': self.display_currency,
            'cad_to_usd_rate': float(self.cad_to_usd_rate),
            'exchange_buffer_percent': float(self.exchange_buffer_percent),
            'markup_percent': float(self.markup_percent),
            'fixed_fee_usd': float(self.fixed_fee_usd),
            'minimum_profit_usd': float(self.minimum_profit_usd),
            'rounding_increment': float(self.rounding_increment),
            'customization_file_review_fee_usd': float(self.customization_file_review_fee_usd),
            'customization_design_assist_fee_usd': float(self.customization_design_assist_fee_usd),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
