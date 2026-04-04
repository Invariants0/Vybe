import pytest
from peewee import SqliteDatabase
from backend.app import create_app
from backend.app.config.database import db
from backend.app.models import User, ShortURL, Event, LinkVisit


@pytest.fixture
def client():
    """Create test client with in-memory SQLite database."""
    # Use in-memory SQLite for unit tests
    test_db = SqliteDatabase(':memory:')
    
    app = create_app()
    app.config["TESTING"] = True
    
    # Override database with in-memory SQLite
    db.initialize(test_db)
    
    with app.app_context():
        # Create all tables
        test_db.create_tables([User, ShortURL, LinkVisit, Event])
        
        with app.test_client() as client:
            yield client
        
        test_db.close()


def test_health_check(client):
    """Bronze Tier: Pulse check for /health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "ok"
