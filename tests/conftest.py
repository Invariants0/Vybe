import pytest
from playhouse.pool import PooledPostgresqlDatabase
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

from backend.app import create_app
from backend.app.config.database import db
from backend.app.models import Event, ShortURL, User, LinkVisit
from backend.app.utils import cache


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:16-alpine") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def redis_container():
    with RedisContainer("redis:7-alpine") as redis:
        yield redis


@pytest.fixture(scope="session")
def app(postgres_container):
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
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def clean_database(app, request):
    # Ensure strict test isolation by truncating tables before each test execution.
    # Skip for unit tests - use os.path to handle path separators correctly
    import os
    fspath = str(request.node.fspath)
    if os.sep + "tests" + os.sep + "unit" + os.sep in fspath:
        yield
        return

    if db.is_closed():
        db.connect()

    with db.atomic():
        Event.delete().execute()
        LinkVisit.delete().execute()
        ShortURL.delete().execute()
        User.delete().execute()

    yield


@pytest.fixture(scope="function")
def test_user(client):
    response = client.post("/users", json={"username": "urltester", "email": "url@vybe.local"})
    return response.get_json()


@pytest.fixture
def redis_config(redis_container):
    cache._client = None
    yield {
        "REDIS_ENABLED": True,
        "REDIS_URL": f"redis://{redis_container.get_container_host_ip()}:{redis_container.get_exposed_port(6379)}/0",
        "REDIS_DEFAULT_TTL_SECONDS": 1,
        "REDIS_RETRY_ATTEMPTS": 2,
        "REDIS_RETRY_BACKOFF_SECONDS": 0.01,
    }
    cache._client = None
