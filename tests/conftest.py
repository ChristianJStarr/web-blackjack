import os
import sys
import pytest
from flask import Flask
from blackjack import create_app, db

# Add the project root to the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def app():
    """Create a Flask application configured for testing."""
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    # Create the database and the database tables
    with app.app_context():
        db.create_all()
    
    yield app
    
    # Teardown
    with app.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()


@pytest.fixture
def db_session(app):
    """Creates a new database session for testing."""
    with app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()
        
        # Create a session bound to the connection
        session = db.create_scoped_session(
            options={"bind": connection, "binds": {}}
        )
        
        db.session = session
        
        yield session
        
        # Rollback the transaction and close the connection
        transaction.rollback()
        connection.close()
        session.remove() 