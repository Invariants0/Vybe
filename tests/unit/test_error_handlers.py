from __future__ import annotations

from werkzeug.exceptions import BadRequest

from backend.app.config.errors import AppError


def test_404_error_handler(client):
    """Test 404 error handler for non-existent routes."""
    response = client.get("/nonexistent-route")
    
    assert response.status_code == 404
    data = response.get_json()
    assert data["error"] == "not_found"
    assert "not found" in data["message"].lower()


def test_405_method_not_allowed(client):
    """Test 405 error handler for method not allowed."""
    response = client.post("/health")
    
    assert response.status_code == 405
    data = response.get_json()
    assert data["error"] == "method_not_allowed"


def test_app_error_handler(app):
    """Test custom AppError handler."""
    @app.get("/app-error")
    def app_error():
        raise AppError("broken", status_code=409, error_code="conflict")

    with app.test_client() as client:
        response = client.get("/app-error")

    assert response.status_code == 409
    data = response.get_json()
    assert data["error"] == "conflict"


def test_validation_error_with_details(client):
    """Test validation error returns proper details."""
    response = client.post("/users", json={"username": "test", "email": "invalid"})
    
    assert response.status_code == 422
    data = response.get_json()
    assert data["error"] == "validation_error"
    assert "details" in data
    assert len(data["details"]) > 0


def test_not_found_error(client):
    """Test not found error for non-existent resources."""
    response = client.get("/users/999999")
    
    assert response.status_code == 404
    data = response.get_json()
    assert data["error"] == "not_found"


def test_bad_request_handler(app):
    """Test bad request error handler."""
    @app.get("/bad-request")
    def bad_request():
        raise BadRequest("invalid json")

    with app.test_client() as client:
        response = client.get("/bad-request")

    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "bad_request"


def test_bad_request_malformed_json(client):
    """Test bad request with malformed JSON."""
    response = client.post(
        "/users",
        data='{"username": "test", "email": "test@example.com",}',
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data or "message" in data


def test_unexpected_error_handler(client):
    """Test unexpected error handler."""
    response = client.get("/boom")

    assert response.status_code == 500
    data = response.get_json()
    assert data["status"] == "error"
