import pytest
# Uses 'client' fixture from conftest.py

def test_validation_error_format(client):
    """Gold Tier: Verify Pydantic validation errors return structured JSON."""
    # Send user create with invalid email
    response = client.post("/users", json={"username": "err", "email": "not-an-email"})
    
    assert response.status_code == 422
    data = response.get_json()
    assert data["error"] == "validation_error"
    assert "details" in data
    assert any("email" in d["loc"] for d in data["details"])


def test_malformed_json(client):
    """Gold Tier: Ensure the app handles invalid JSON syntax gracefully."""
    response = client.post("/users", 
                          data='{"username": "err", "email": "test@vybe.local",}', # Trailing comma
                          content_type='application/json')
    
    # Flask typically returns 400 for malformed JSON
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data or "message" in data


def test_internal_error_catch(client, monkeypatch):
    """Gold Tier: Verify that a server-side exception returns a polite 500 JSON, not a stack trace."""
    from backend.app.services.user_service import UserService
    
    def mock_fail(*args, **kwargs):
        raise RuntimeError("Something went horribly wrong internally!")
    
    # Force the service layer to crash
    monkeypatch.setattr(UserService, "get_all_users", mock_fail)
    
    response = client.get("/users")
    assert response.status_code == 500
    data = response.get_json()
    assert data["status"] == "error"
    assert "An internal server error occurred" in data["message"]
