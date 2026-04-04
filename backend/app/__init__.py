from dotenv import load_dotenv
from flask import Flask, jsonify
import os

from backend.app.config import create_tables, get_config, init_db, ping_db, register_error_handlers
from backend.app.middleware import register_middleware
from backend.app.routes import register_routes


def create_app():
    # Load .env file from backend directory
    load_dotenv("backend/.env")

    app = Flask(__name__)
    config = get_config()
    app.config.from_object(config)
    
    # Override with environment variables to ensure they're fresh after load_dotenv
    app.config["DATABASE_PORT"] = int(os.getenv("DATABASE_PORT", 5432))
    app.config["DATABASE_HOST"] = os.getenv("DATABASE_HOST", "localhost")
    app.config["DATABASE_NAME"] = os.getenv("DATABASE_NAME", "hackathon_db")
    app.config["DATABASE_USER"] = os.getenv("DATABASE_USER", "postgres")
    app.config["DATABASE_PASSWORD"] = os.getenv("DATABASE_PASSWORD", "postgres")

    init_db(app)

    from backend.app import models  # noqa: F401 - ensure model registration before table setup

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
