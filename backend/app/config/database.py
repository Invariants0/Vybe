from peewee import DatabaseProxy, Model
from playhouse.pool import PooledPostgresqlDatabase
from prometheus_client import Gauge

db = DatabaseProxy()

DB_POOL_CONNECTIONS_OPEN = Gauge(
    "db_pool_connections_open",
    "Number of database connections tracked by the Peewee pool.",
)
DB_POOL_CONNECTIONS_IN_USE = Gauge(
    "db_pool_connections_in_use",
    "Number of database connections currently in use.",
)
DB_POOL_MAX_CONNECTIONS = Gauge(
    "db_pool_max_connections",
    "Configured database connection pool size.",
)


class BaseModel(Model):
    class Meta:
        database = db


def init_db(app):
    database = PooledPostgresqlDatabase(
        app.config["DATABASE_NAME"],
        host=app.config["DATABASE_HOST"],
        port=app.config["DATABASE_PORT"],
        user=app.config["DATABASE_USER"],
        password=app.config["DATABASE_PASSWORD"],
        max_connections=app.config["DB_MAX_CONNECTIONS"],
        stale_timeout=app.config["DB_STALE_TIMEOUT_SECONDS"],
        timeout=app.config["DB_CONNECTION_TIMEOUT_SECONDS"],
    )
    db.initialize(database)
    record_pool_metrics()

    @app.before_request
    def _db_connect():
        try:
            db.connect(reuse_if_open=True)
            record_pool_metrics()
        except Exception as e:
            app.logger.error(f"Failed to connect to database: {e}")

    @app.teardown_request
    def _db_close(_exc):
        if not db.is_closed():
            try:
                db.close()
            except Exception:
                pass
        record_pool_metrics()


def create_tables(safe=True):
    from backend.app.models import Event, LinkVisit, ShortURL, User

    if db.is_closed():
        db.connect(reuse_if_open=True)
    # Order matters: User before ShortURL (FK), ShortURL before Event/LinkVisit (FK)
    db.create_tables([User, ShortURL, LinkVisit, Event], safe=safe)


def ping_db():
    if db.is_closed():
        db.connect(reuse_if_open=True)
    db.execute_sql("SELECT 1")
    record_pool_metrics()


def get_pool_snapshot() -> dict[str, int]:
    database = getattr(db, "obj", None)
    if database is None:
        return {"open": 0, "in_use": 0, "max": 0}

    open_connections = len(getattr(database, "_connections", []))
    in_use_connections = len(getattr(database, "_in_use", {}))
    max_connections = int(
        getattr(database, "_max_connections", getattr(database, "max_connections", 0))
        or 0
    )
    return {
        "open": open_connections,
        "in_use": in_use_connections,
        "max": max_connections,
    }


def record_pool_metrics() -> dict[str, int]:
    snapshot = get_pool_snapshot()
    DB_POOL_CONNECTIONS_OPEN.set(snapshot["open"])
    DB_POOL_CONNECTIONS_IN_USE.set(snapshot["in_use"])
    DB_POOL_MAX_CONNECTIONS.set(snapshot["max"])
    return snapshot
