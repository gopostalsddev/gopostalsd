
from server.controllers import Result
from server.controllers.user_controller import UserController, UserSuccesses, UserErrors
from server.models import User, Role, Address
from server import database as db


def create_role_and_addresses():
    # Create role
    
    role = Role(name="Guest", description="A user who does not have an account")
    db.session.add(role)
    db.session.commit()
     
    # Create addresses
    shipping_address = Address(
        street="123 Shipping Lane", city="San Diego", state="CA",
        zip_code=92101, country="USA"
    )

    # Billing addresses
    billing_address = Address(
        street="456 Billing Ave", city="San Diego", state="CA",
        zip_code=92101, country="USA"
    )
    db.session.add_all([shipping_address, billing_address])
    db.session.commit()

    return role, shipping_address, billing_address

def test_create_user_success(client):
    role, shipping_address, billing_address = create_role_and_addresses()

    # Mock user data
    user_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email_address": "john.doe@testing.com",
        "role_id": role.id,
        "shipping_address_id": shipping_address.id,
        "billing_address_id": billing_address.id
    }

    result = UserController.create_user(user_data)

    assert isinstance(result, Result)
    assert result.status is True
    assert result.data.first_name == user_data["first_name"]
    assert result.data.last_name == user_data["last_name"]
    assert result.data.email_address == user_data["email_address"]
    assert result.data.role_id == user_data["role_id"]
    assert result.data.shipping_address_id == user_data["shipping_address_id"]
    assert result.data.billing_address_id == user_data["billing_address_id"]
    assert result.error is None

def test_create_user_missing_fields(client):
    user_data = {
        "first_name": "Jane"
        # Missing last_name and email_address
    }

    result = UserController.create_user(user_data)

    assert isinstance(result, Result)
    assert result.status is False
    assert result.error == UserErrors.MISSING_REQUIRED_FIELDS
    assert result.data is None

def test_create_user_already_exists(client):

    role, shipping_address, billing_address = create_role_and_addresses()

    user_data = {
        "first_name": "Alice",
        "last_name": "Smith",
        "email_address": "alice@example.com",
        "role_id": role.id,
        "shipping_address_id": shipping_address.id,
        "billing_address_id": billing_address.id
    }

    # First insertion should succeed
    UserController.create_user(user_data)
    
    # Duplicate insertion should fail
    result = UserController.create_user(user_data)

    assert isinstance(result, Result)
    assert result.status is False
    assert result.error == UserErrors.USER_ALREADY_EXISTS
    assert result.data is None

def test_create_user_invalid_role(client):
    _, shipping_address, billing_address = create_role_and_addresses()

    user_data = {
        "first_name": "Bob",
        "last_name": "Marley",
        "email_address": "bob.marley@example.com",
        "role_id": 9999, # Invalid role ID
        "shipping_address_id": shipping_address.id,
        "billing_address_id": billing_address.id
    }

    result = UserController.create_user(user_data)

    assert isinstance(result, Result)
    assert result.status is False
    assert result.error == UserErrors.INVALID_ROLE
    assert result.data is None

def test_create_user_invalid_address(client):
    role, _,_ = create_role_and_addresses()

    user_data = {
        "first_name": "Chanrlie",
        "last_name": "Chaplin",
        "email_address": "charlie.chaplin@example.com",
        "role_id" : role.id,
        "shipping_address_id": 9999, # Invalid address ID
        "billing_address_id": 9999   # Invalid address ID
    }

    result = UserController.create_user(user_data)

    assert isinstance(result, Result)
    assert result.status is False
    assert result.error == UserErrors.INVALID_ADDRESS
    assert result.data is None 

def test_get_all_users(client):
    role, shipping_address, billing_address = create_role_and_addresses()

    # Add mock users
    user1 = User(first_name="Test", last_name="User", email_address="test1@testing.com",
                 role_id=role.id, shipping_address_id=shipping_address.id, billing_address_id=billing_address.id)
    user2 = User(first_name="Another", last_name="User", email_address="test2@testing.com",
                 role_id=role.id, shipping_address_id=shipping_address.id, billing_address_id=billing_address.id)
    db.session.add_all([user1, user2])
    db.session.commit()

    result = UserController.get_all_users()

    assert isinstance(result, Result)
    assert result.status is True
    assert  isinstance(result.data, list)
    assert len(result.data) == 2
    assert result.error is None

def test_delete_user_success(client):
    role, shipping_address, billing_address = create_role_and_addresses()

    # Mock user data
    user_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email_address": "john.doe@testing.com",
        "role_id": role.id,
        "shipping_address_id": shipping_address.id,
        "billing_address_id": billing_address.id
    }

    UserController.create_user(user_data)
    result = UserController.delete_user(user_data["email_address"])

    assert isinstance(result, Result)
    assert result.status is True
    assert result.data == UserSuccesses.USER_DELETED_SECCESSFULLY
    assert result.error is None

def test_delete_user_not_found(client):
    result = UserController.delete_user("nonexistantuser@testing.com")

    assert isinstance(result, Result)
    assert result.status is False
    assert result.error == UserErrors.USER_NOT_FOUND
    assert result.data is None

def test_delete_user_invalid_email_address(client):
    invalid_email_address = "Invalid-email-format"
    result = UserController.delete_user(invalid_email_address)
    
    assert isinstance(result, Result)
    assert result.status is False
    assert result.error == UserErrors.INVALID_EMAIL_ADDRESS
    assert result.data is None