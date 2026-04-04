"""Unit tests for error handlers."""
import pytest
from peewee import SqliteDatabase
from backend.app import create_app
from backend.app.config.database import db
from backend.app.config.errors import AppError, ValidationError, NotFoundError, ConflictError
from backend.app.models import User, ShortURL, Event, LinkVisit


@pytest.fixture
def client():
    """Create test client with in-memory SQLite database."""
    test_db = SqliteDatabase(':memory:')
    
    app = create_app()
    app.config["TESTING"] = True
    
    db.initialize(test_db)
    
    with app.app_context():
        test_db.create_tables([User, ShortURL, LinkVisit, Event])
        
        with app.test_client() as client:
            yield client
        
        test_db.close()


class TestErrorHandlers:
    """Test custom error handlers."""
    
    def test_404_error_handler(self, client):
        """Test 404 error returns proper JSON."""
        response = client.get("/nonexistent-route")
        assert response.status_code == 404
        data = response.get_json()
        assert data["error"] == "not_found"
        assert "not found" in data["message"].lower()
    
    def test_405_method_not_allowed(self, client):
        """Test 405 error for unsupported HTTP methods."""
        # POST to health endpoint which only supports GET
        response = client.post("/health")
        assert response.status_code == 405
        data = response.get_json()
        assert data["error"] == "method_not_allowed"
    
    def test_app_error_handler(self, client):
        """Test custom AppError is handled properly."""
        # This is tested indirectly through validation errors
        response = client.post("/users", json={"username": "test"})  # Missing email
        assert response.status_code == 422
        data = response.get_json()
        assert "error" in data or "details" in data
    
    def test_validation_error_with_details(self, client):
        """Test validation error returns details."""
        response = client.post("/users", json={"username": "test", "email": "invalid"})
        assert response.status_code == 422
        data = response.get_json()
        assert data["error"] == "validation_error"
        assert "details" in data
        assert len(data["details"]) > 0
    
    def test_not_found_error(self, client):
        """Test not found error returns 404."""
        response = client.get("/users/999999")
        assert response.status_code == 404
        data = response.get_json()
        assert data["error"] == "not_found"
    
    def test_bad_request_malformed_json(self, client):
        """Test malformed JSON returns 400."""
        response = client.post(
            "/users",
            data='{"username": "test", "email": "test@example.com",}',  # Trailing comma
            content_type='application/json'
        )
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data or "message" in data
