
from enum import Enum
from server.config import database as db
from server.models.auth import User, Role, Address
from server.controllers.helpers import Result
import re

class UserErrors(Enum):
    FAILED_TO_GET_ALL_USERS = "Failed to get all users!"
    MISSING_REQUIRED_FIELDS = "One ore more required fields missing!"
    USER_ALREADY_EXISTS = "User with this email already exists!"
    USER_NOT_FOUND = "User not found!"
    INVALID_ROLE = "Invalid role specified!"
    INVALID_ADDRESS = "Invalid address specified!"
    INVALID_EMAIL = "Invalid email format!"

class UserSuccesses(Enum):
    USER_DELETED_SECCESSFULLY = "User deleted successfully!"

class UserController:

    @staticmethod
    def get_all_users() -> Result:
        result = Result()
        data = User.query.all()

        if data:
            result.data = data
        else:
            result.status = False
            result.error = UserErrors.FAILED_TO_GET_ALL_USERS
        
        return result
    
    @staticmethod
    def create_user(data: dict) -> Result:
        result = Result()
        
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        role_id = data.get('role_id')
        shipping_address_id = data.get('shipping_address_id')
        billing_address_id = data.get('billing_address_id')

        if None in [first_name, last_name, email, role_id, shipping_address_id, billing_address_id]:
            result.status = False
            result.error = UserErrors.MISSING_REQUIRED_FIELDS
            return result
            
        user_exists = db.session.query(
            db.exists().where(User.email == email)
        ).scalar()
        if user_exists:
            result.status = False
            result.error = UserErrors.USER_ALREADY_EXISTS
            return result
        
        role = db.session.get(Role, role_id)
        if not role:
            result.status = False
            result.error = UserErrors.INVALID_ROLE
            return result
        
        shipping_address = db.session.get(Address, shipping_address_id)
        billing_address = db.session.get(Address, billing_address_id)
        if not shipping_address or not billing_address:
            result.status = False
            result.error = UserErrors.INVALID_ADDRESS
            return result
        
        try:
            new_user = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                role=role,
                shipping_address=shipping_address,
                billing_address=billing_address
            )
            db.session.add(new_user)
            db.session.commit()
            result.data = new_user

        except Exception as e:
            result.status = False
            result.error = str(e)

        return result

    @staticmethod
    def delete_user(email: str) -> Result:
        result = Result()

        email_regex = r'^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            result.status = False
            result.error = UserErrors.INVALID_EMAIL
            return result
        
        user = User.query.filter_by(email=email).first()
        if not user:
            result.status = False
            result.error = UserErrors.USER_NOT_FOUND
            return result
        
        db.session.delete(user)
        db.session.commit()

        result.status = True
        result.data = UserSuccesses.USER_DELETED_SECCESSFULLY
        result.error = None
        return result


