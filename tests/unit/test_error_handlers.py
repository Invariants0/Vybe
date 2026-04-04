import pytest


class TestErrorHandlers:
    
    def test_404_error_handler(self, client):
        response = client.get("/nonexistent-route")
        assert response.status_code == 404
        data = response.get_json()
        assert data["error"] == "not_found"
        assert "not found" in data["message"].lower()
    
    def test_405_method_not_allowed(self, client):
        response = client.post("/health")
        assert response.status_code == 405
        data = response.get_json()
        assert data["error"] == "method_not_allowed"
    
    def test_app_error_handler(self, client):
        response = client.post("/users", json={"username": "test"})
        assert response.status_code == 422
        data = response.get_json()
        assert "error" in data or "details" in data
    
    def test_validation_error_with_details(self, client):
        response = client.post("/users", json={"username": "test", "email": "invalid"})
        assert response.status_code == 422
        data = response.get_json()
        assert data["error"] == "validation_error"
        assert "details" in data
        assert len(data["details"]) > 0
    
    def test_not_found_error(self, client):
        response = client.get("/users/999999")
        assert response.status_code == 404
        data = response.get_json()
        assert data["error"] == "not_found"
    
    def test_bad_request_malformed_json(self, client):
        response = client.post(
            "/users",
            data='{"username": "test", "email": "test@example.com",}',
            content_type='application/json'
        )
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data or "message" in data
