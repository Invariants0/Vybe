import json
import pytest


def test_create_user(client):
    response = client.post("/users", json={"username": "testuser", "email": "test@vybe.local"})
    assert response.status_code == 201
    data = response.get_json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@vybe.local"
    assert "id" in data


def test_create_user_invalid_schema(client):
    response = client.post("/users", json={"username": "testuser", "email": "invalid-email"})
    assert response.status_code == 422
    assert response.get_json()["error"] == "validation_error"


def test_list_users(client):
    client.post("/users", json={"username": "user1", "email": "1@vybe.local"})
    client.post("/users", json={"username": "user2", "email": "2@vybe.local"})
    
    response = client.get("/users")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) >= 2


def test_get_user(client):
    create_response = client.post("/users", json={"username": "getuser", "email": "get@vybe.local"})
    user_id = create_response.get_json()["id"]

    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.get_json()["username"] == "getuser"


def test_get_user_not_found(client):
    response = client.get("/users/999999")
    assert response.status_code == 404


def test_update_user(client):
    create_response = client.post("/users", json={"username": "upuser", "email": "up@vybe.local"})
    user_id = create_response.get_json()["id"]

    response = client.put(f"/users/{user_id}", json={"username": "upuser_new"})
    assert response.status_code == 200
    assert response.get_json()["username"] == "upuser_new"
    
    # Email should be unchanged because it wasn't provided
    assert response.get_json()["email"] == "up@vybe.local"
