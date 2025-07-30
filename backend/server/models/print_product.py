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
    
    