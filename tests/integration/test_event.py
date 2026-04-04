import pytest
# Uses 'client' fixture from conftest.py

def test_event_logged_on_create(client):
    """Silver Tier: Verify 'created' event is logged in DB."""
    # Create user
    user_resp = client.post("/users", json={"username": "eventer", "email": "event@vybe.local"})
    user_id = user_resp.get_json()["id"]
    
    # Create URL
    url_resp = client.post("/urls", json={
        "user_id": user_id,
        "original_url": "https://vybe.io",
        "title": "Vybe"
    })
    url_id = url_resp.get_json()["id"]
    
    # Check events via API (EventController)
    event_resp = client.get("/events")
    assert event_resp.status_code == 200
    events = event_resp.get_json()
    
    # Should see at least one 'created' event for this URL
    url_events = [e for e in events if e["short_url_id"] == url_id and e["event_type"] == "created"]
    assert len(url_events) == 1
    assert url_events[0]["user_id"] == user_id


def test_event_logged_on_redirect(client):
    """Silver Tier: Verify 'accessed' event is logged when redirection occurs."""
    # Setup user/url
    user_resp = client.post("/users", json={"username": "redir", "email": "redir@vybe.local"})
    user_id = user_resp.get_json()["id"]
    url_resp = client.post("/urls", json={"user_id": user_id, "original_url": "https://google.com"})
    url_id = url_resp.get_json()["id"]
    short_code = url_resp.get_json()["short_code"]
    
    # Perform redirect
    client.get(f"/{short_code}")
    
    # Check events
    event_resp = client.get("/events")
    events = event_resp.get_json()
    
    # Filter for 'accessed' events for this URL
    accessed_events = [e for e in events if e["short_url_id"] == url_id and e["event_type"] == "accessed"]
    assert len(accessed_events) == 1
