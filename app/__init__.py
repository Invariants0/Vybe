from dotenv import load_dotenv
from flask import Flask, jsonify

from app.config import get_config
from app.database import create_tables, init_db, ping_db
from app.errors import register_error_handlers
from app.middleware import register_middleware
from app.routes import register_routes


def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object(get_config())

    init_db(app)

    from app import models  # noqa: F401 - ensure model registration before table setup

    register_middleware(app)
    register_error_handlers(app)
    register_routes(app)

    if app.config["AUTO_CREATE_TABLES"]:
        create_tables()

    @app.get("/health")
    def health():
        return jsonify(status="ok", service=app.config["APP_NAME"])

    @app.get("/ready")
    def readiness():
        ping_db()
        return jsonify(status="ready", service=app.config["APP_NAME"])

    return app
