from dotenv import load_dotenv
from flask import Flask, jsonify
import os

try:
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration

    _SENTRY_AVAILABLE = True
except ImportError:
    sentry_sdk = None  # type: ignore[assignment]
    FlaskIntegration = None  # type: ignore[assignment]
    _SENTRY_AVAILABLE = False

from backend.app.config import (
    create_tables,
    get_config,
    init_db,
    ping_db,
    register_error_handlers,
)
from backend.app.middleware import register_middleware
from backend.app.routes import register_routes


def create_app():
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if os.path.exists(env_path):
        load_dotenv(env_path)
    else:
        load_dotenv()

    # Initialize Sentry for error tracking
    sentry_dsn = os.getenv("SENTRY_DSN")
    if sentry_dsn and _SENTRY_AVAILABLE:
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[FlaskIntegration()],
            traces_sample_rate=0.1,
            profiles_sample_rate=0.1,
            environment=os.getenv("FLASK_ENV", "development"),
            release=os.getenv("APP_VERSION", "unknown"),
            send_default_pii=False,
        )

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
        try:
            create_tables()
        except Exception as e:
            app.logger.warning(
                f"Failed to create tables during startup: {e}. Tables will be created on first request."
            )

    @app.get("/health")
    def health():
        return jsonify(status="ok", service=app.config["APP_NAME"])

    @app.get("/ready")
    def readiness():
        try:
            ping_db()
            return jsonify(status="ready", service=app.config["APP_NAME"])
        except Exception as e:
            app.logger.error(f"Readiness check failed: {e}")
            return jsonify(status="not ready", error=str(e)), 503

    return app
