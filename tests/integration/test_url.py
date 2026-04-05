def test_create_url(client, test_user):
    user_id = test_user["id"]
    response = client.post("/urls", json={
        "user_id": user_id,
        "original_url": "https://google.com/search?q=vybe",
        "title": "Google Search"
    })
    
    assert response.status_code == 201
    data = response.get_json()
    assert data["original_url"] == "https://google.com/search?q=vybe"
    assert data["user_id"] == user_id
    assert "short_code" in data
    assert data["is_active"] is True


def test_create_url_invalid_url(client, test_user):
    user_id = test_user["id"]
    response = client.post("/urls", json={
        "user_id": user_id,
        "original_url": "not-a-valid-url"
    })
    assert response.status_code == 422
    assert response.get_json()["error"] == "validation_error"


def test_redirect(client, test_user):
    user_id = test_user["id"]
    create_response = client.post("/urls", json={
        "user_id": user_id,
        "original_url": "https://mlh.io"
    })
    short_code = create_response.get_json()["short_code"]

    response = client.get(f"/{short_code}")
    assert response.status_code == 302
    assert response.headers["Location"] == "https://mlh.io"


def test_redirect_not_found(client):
    response = client.get("/invalid_code_no_exist")
    assert response.status_code == 404

