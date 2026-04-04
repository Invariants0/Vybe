import pytest
from backend.app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_check(client):
    """Bronze Tier: Pulse check for /health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "ok"
