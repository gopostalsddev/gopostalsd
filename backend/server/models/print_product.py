from datetime import datetime, timezone
from server.config import database as db

class PrintProductCategory(db.Model):
    __tablename__ = "print_product_categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True) 
    image = db.Column(db.String(512), nullable=True)  
    enabled = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=db.func.now(), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=db.func.now(), onupdate=db.func.now(), nullable=False)

    def to_dict(self):
        """Convert object to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "image": self.image,
            "enabled": self.enabled,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<PrintProductCategory {self.name}>"


class PrintProductType(db.Model):
    __tablename__ = "print_product_types"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('print_product_categories.id'), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(512), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=db.func.now(), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=db.func.now(), onupdate=db.func.now(), nullable=False)

    # Relationship
    category = db.relationship('PrintProductCategory', backref='product_types')

    def to_dict(self):
        """Convert object to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "category_id": self.category_id,
            "description": self.description,
            "image": self.image,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<PrintProductType {self.name}>"


class PrintProduct(db.Model):
    __tablename__ = "print_products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    sku = db.Column(db.String(255), unique=True, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('print_product_categories.id'), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('print_product_types.id'), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(512), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=db.func.now(), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=db.func.now(), onupdate=db.func.now(), nullable=False)

    # Relationships
    category = db.relationship('PrintProductCategory', backref='products')
    product_type = db.relationship('PrintProductType', backref='products')

    def to_dict(self):
        """Convert object to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "sku": self.sku,
            "category_id": self.category_id,
            "type_id": self.type_id,
            "description": self.description,
            "image": self.image,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<PrintProduct {self.name}>"