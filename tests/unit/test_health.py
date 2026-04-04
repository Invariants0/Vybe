import pytest

# Uses 'client' fixture from parent conftest.py (PostgreSQL testcontainer)


def test_health_check(client):
    """Bronze Tier: Pulse check for /health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "ok"
