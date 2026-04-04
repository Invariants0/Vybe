from peewee import DatabaseProxy, Model
from playhouse.pool import PooledPostgresqlDatabase

db = DatabaseProxy()


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

    @app.before_request
    def _db_connect():
        db.connect(reuse_if_open=True)

    @app.teardown_request
    def _db_close(_exc):
        if not db.is_closed():
            db.close()


def create_tables(safe=True):
    from backend.app.models import Event, LinkVisit, ShortURL, User

    if db.is_closed():
        db.connect(reuse_if_open=True)
    # Order matters: User before ShortURL (FK), ShortURL before Event (FK)
    db.create_tables([User, ShortURL, LinkVisit, Event], safe=safe)


def ping_db():
    if db.is_closed():
        db.connect(reuse_if_open=True)
    db.execute_sql("SELECT 1")
