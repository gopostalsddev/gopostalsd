from server import database as db
from datetime import datetime
from sqlalchemy.sql import func


class Vendor(db.Model):
    """Vendor model for tracking product sources"""
    __tablename__ = 'vendors'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=func.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=func.now(), onupdate=func.now())
    
    # Relationships
    products = db.relationship('PrintProduct', back_populates='vendor')
    
    def to_dict(self):
        """Convert vendor to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class PrintProductCategory(db.Model):
    """Print product category model"""
    __tablename__ = 'print_product_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(500), nullable=True)
    enabled = db.Column(db.Boolean, default=False, nullable=False)
    product_classification_status = db.Column(db.JSON, default={
        "all_classified": False,
        "total_products": 0,
        "classified_products": 0,
        "unclassified_products": 0
    }, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=func.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=func.now(), onupdate=func.now())
    
    # Relationships
    product_types = db.relationship('PrintProductType', back_populates='category', cascade='all, delete-orphan')
    products = db.relationship('PrintProduct', back_populates='category', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert category to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'image': self.image,
            'enabled': self.enabled,
            'is_enabled': self.enabled,
            'product_classification_status': self.product_classification_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class PrintProductType(db.Model):
    """Print product type model"""
    __tablename__ = 'print_product_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(500), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('print_product_categories.id'), nullable=True)  # NULL for wildcard type
    created_at = db.Column(db.DateTime, nullable=False, default=func.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=func.now(), onupdate=func.now())
    
    # Relationships
    category = db.relationship('PrintProductCategory', back_populates='product_types')
    products = db.relationship('PrintProduct', back_populates='product_type')
    
    def to_dict(self):
        """Convert product type to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'image': self.image,
            'category_id': self.category_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class PrintProduct(db.Model):
    """Print product model"""
    __tablename__ = 'print_products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    sku = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(500), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('print_product_categories.id'), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('print_product_types.id'), nullable=False, default=0)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False, default=0)
    vendor_product_id = db.Column(db.String(255), nullable=True)  # ID from vendor's system
    created_at = db.Column(db.DateTime, nullable=False, default=func.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=func.now(), onupdate=func.now())
    
    # Relationships
    category = db.relationship('PrintProductCategory', back_populates='products')
    product_type = db.relationship('PrintProductType', back_populates='products')
    vendor = db.relationship('Vendor', back_populates='products')
    
    def to_dict(self):
        """Convert product to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'sku': self.sku,
            'description': self.description,
            'image': self.image,
            'category_id': self.category_id,
            'type_id': self.type_id,
            'vendor_id': self.vendor_id,
            'vendor_product_id': self.vendor_product_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }