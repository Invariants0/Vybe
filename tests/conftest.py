import os
import pytest
from playhouse.pool import PooledPostgresqlDatabase
from testcontainers.postgres import PostgresContainer

from backend.app import create_app
from backend.app.config.database import db
from backend.app.models import Event, ShortURL, User, LinkVisit


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:16-alpine") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def app(postgres_container):
    """Initialize the Flask application configured for containerized testing."""
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
    
    # Use the testcontainer database pool
    db.initialize(test_db)
    
    with app.app_context():
        test_db.create_tables([User, ShortURL, LinkVisit, Event])
        yield app
        test_db.close()


@pytest.fixture(scope="function")
def client(app):
    """Provides a Flask test client for integration testing."""
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def clean_database(app):
    """Ensure strict test isolation by truncating tables before each test execution."""
    if db.is_closed():
        db.connect()
    
    with db.atomic():
        Event.delete().execute()
        LinkVisit.delete().execute()
        ShortURL.delete().execute()
        User.delete().execute()


@pytest.fixture(scope="function")
def test_user(client):
    """Bootstrap a standard test user for authenticated request flows."""
    response = client.post("/users", json={"username": "urltester", "email": "url@vybe.local"})
    return response.get_json()

