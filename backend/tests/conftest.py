import pytest
from server import create_server, database as db


# Define the app fixture required by pytest-flask
@pytest.fixture
def app():
    # Create a Flask application instance in testing mode
    test_server = create_server("testing")
    # Set up the application context
    with test_server.app_context():

        print("TABLES")
        for table in db.metadata.tables.keys():
            print(table)

        db.create_all()       # Create tables before tests run
        yield test_server     # This makes the app available to tests
        db.drop_all()         # Drop tables after tests complete

# Define the client fixture that depends on the app fixture
@pytest.fixture
def client(app):
    return app.test_client()
