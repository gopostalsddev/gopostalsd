from server import database as db
from datetime import datetime, timezone


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer,primary_key=True )
    first_name = db.Column(db.String(60), nullable=False)
    last_name = db.Column(db.String(60), nullable=False)
    email_address = db.Column(db.String(120), unique=True, nullable=False)
    creation_date = db.Column(db.DateTime(timezone=True), default=db.func.now(), nullable=False)

    # Foreign key for addresses
    shipping_address_id = db.Column(db.Integer, db.ForeignKey('addresses.id'), nullable = False)
    billing_address_id = db.Column(db.Integer, db.ForeignKey('addresses.id'), nullable = False)

    # Relationship to address model
    shipping_address = db.relationship('Address', foreign_keys=[shipping_address_id], backref='shipping_users')
    billing_address = db.relationship('Address', foreign_keys=[billing_address_id], backref='billing_users')

    # Foreign key to Role
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    role = db.relationship('Role', backref='users')

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(16), nullable=False)
    description = db.Column(db.String(120), nullable=True)

class Address(db.Model):
    __tablename__ = 'addresses'

    id = db.Column(db.Integer, primary_key = True)
    street = db.Column(db.String(180), nullable = False)
    city = db.Column(db.String(180), nullable = False)
    state = db.Column(db.String(120), nullable = False)
    zip_code = db.Column(db.Integer, nullable = False)
    country = db.Column(db.String(180), nullable = False)
    apt = db.Column(db.String, nullable = True)

    def __repr__(self):
        return f"<Address {self.street}, {self.city}, {self.country}>"

class Account(db.Model):
    __tablename__ = 'accounts'
    username = db.Column(
        db.String(100),
        primary_key = True
    )

class HashingAlgorithm(db.Model):
    __tablename__ = 'hashing_algorithms'
    id = db.Column(
        db.Integer,
        primary_key = True
    )

