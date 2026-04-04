import os
import pytest
from peewee import SqliteDatabase

from backend.app import create_app
from backend.app.config.database import db
from backend.app.models import Event, ShortURL, User


@pytest.fixture(scope="session")
def app():
    """Create Flask app with in-memory SQLite for testing."""
    # Use in-memory SQLite for testing (no Docker required)
    test_db = SqliteDatabase(":memory:")
    
    app = create_app({
        "TESTING": True,
    })
    
    # Override database with in-memory SQLite
    db.initialize(test_db)
    
    with app.app_context():
        # Create all tables
        test_db.create_tables([User, ShortURL, Event])
        yield app
        test_db.close()


@pytest.fixture(scope="function")
def client(app):
    """Test client for performing HTTP requests."""
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def clean_database(app):
    """Clean all tables before every test runs to ensure test isolation."""
    if db.is_closed():
        db.connect()
    
    with db.atomic():
        Event.delete().execute()
        ShortURL.delete().execute()
        User.delete().execute()


@pytest.fixture(scope="function")
def test_user(client):
    """Create a test user for integration tests."""
    response = client.post("/users", json={"username": "urltester", "email": "url@vybe.local"})
    return response.get_json()
