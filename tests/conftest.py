import os
import pytest
from playhouse.pool import PooledPostgresqlDatabase
from testcontainers.postgres import PostgresContainer

from backend.app import create_app
from backend.app.config.database import db
from backend.app.models import Event, ShortURL, User, LinkVisit


@pytest.fixture(scope="session")
def postgres_container():
    """Start a PostgreSQL container for testing."""
    with PostgresContainer("postgres:16-alpine") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def app(postgres_container):
    """Create Flask app with PostgreSQL for testing."""
    # Get connection details from testcontainer
    test_db = PooledPostgresqlDatabase(
        postgres_container.dbname,
        host=postgres_container.get_container_host_ip(),
        port=postgres_container.get_exposed_port(5432),
        user=postgres_container.username,
        password=postgres_container.password,
        max_connections=5,
        stale_timeout=300,
        timeout=10,
    )
    
    app = create_app()
    app.config["TESTING"] = True
    
    # Override database with PostgreSQL testcontainer
    db.initialize(test_db)
    
    with app.app_context():
        # Create all tables
        test_db.create_tables([User, ShortURL, LinkVisit, Event])
        yield app
        test_db.close()


@pytest.fixture(scope="function")
def client(app):
    """Test client for performing HTTP requests."""
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def clean_database(app):
    """Clean all tables before every test runs to ensure test isolation."""
    if db.is_closed():
        db.connect()
    
    with db.atomic():
        Event.delete().execute()
        LinkVisit.delete().execute()
        ShortURL.delete().execute()
        User.delete().execute()


@pytest.fixture(scope="function")
def test_user(client):
    """Create a test user for integration tests."""
    response = client.post("/users", json={"username": "urltester", "email": "url@vybe.local"})
    return response.get_json()
