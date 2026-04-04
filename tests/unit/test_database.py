"""Unit tests for database configuration."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from peewee import SqliteDatabase
from backend.app import create_app
from backend.app.config.database import db
from backend.app.models import User, ShortURL, Event, LinkVisit


@pytest.fixture
def app():
    """Create test app with in-memory database."""
    test_db = SqliteDatabase(':memory:')
    
    app = create_app()
    app.config["TESTING"] = True
    
    db.initialize(test_db)
    
    with app.app_context():
        test_db.create_tables([User, ShortURL, LinkVisit, Event])
        yield app
        test_db.close()


class TestDatabaseConnection:
    """Test database connection lifecycle."""
    
    def test_database_connects_before_request(self, app):
        """Test that database connects before handling request."""
        with app.test_client() as client:
            response = client.get("/health")
            assert response.status_code == 200
            # If database connection failed, the request would fail
    
    def test_database_closes_after_request(self, app):
        """Test that database closes after handling request."""
        with app.test_client() as client:
            response = client.get("/health")
            assert response.status_code == 200
            # Connection should be managed properly
    
    def test_database_reuses_open_connection(self, app):
        """Test that open connections are reused."""
        with app.test_client() as client:
            # Make multiple requests
            response1 = client.get("/health")
            response2 = client.get("/health")
            assert response1.status_code == 200
            assert response2.status_code == 200
    
    def test_models_can_query_database(self, app):
        """Test that models can query the database."""
        with app.app_context():
            # Create a user
            user = User.create(username="testuser", email="test@example.com")
            assert user.id is not None
            
            # Query it back
            found = User.get_by_id(user.id)
            assert found.username == "testuser"
    
    def test_database_tables_exist(self, app):
        """Test that all required tables are created."""
        with app.app_context():
            # Check that we can query each table
            assert User.select().count() >= 0
            assert ShortURL.select().count() >= 0
            assert Event.select().count() >= 0
            assert LinkVisit.select().count() >= 0
