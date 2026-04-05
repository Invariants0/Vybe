def test_validation_error_format(client):
    response = client.post("/users", json={"username": "err", "email": "not-an-email"})

    assert response.status_code == 422
    data = response.get_json()
    assert data["error"] == "validation_error"
    assert "details" in data
    assert any("email" in d["loc"] for d in data["details"])


def test_malformed_json(client):
    response = client.post(
        "/users",
        data='{"username": "err", "email": "test@vybe.local",}',
        content_type="application/json",
    )

    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data or "message" in data


def test_internal_error_catch(client, monkeypatch):
    from backend.app.services.user_service import UserService

    def mock_fail(*args, **kwargs):
        raise RuntimeError("Something went horribly wrong internally!")

    monkeypatch.setattr(UserService, "get_all_users", mock_fail)

    response = client.get("/users")
    assert response.status_code == 500
    data = response.get_json()
    assert data["status"] == "error"
    assert "An internal server error occurred" in data["message"]
