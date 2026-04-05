from __future__ import annotations

import pytest
from flask import Flask, jsonify, request

from backend.app.config.errors import register_error_handlers
from backend.app.middleware import register_middleware
from backend.app.routes.metrics_routes import init_metrics, metrics_bp
from backend.app.utils import cache


@pytest.fixture(autouse=True)
def reset_cache_client():
    cache._client = None
    yield
    cache._client = None


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config.update(
        TESTING=True,
        APP_NAME="vybe-shortener",
        LOG_LEVEL="INFO",
        SENTRY_DSN="",
        AUTH_ENABLED=False,
        API_AUTH_TOKEN="",
        API_AUTH_TOKENS="",
        RATE_LIMIT_ENABLED=True,
        RATE_LIMIT_STORAGE_URI="memory://",
        RATE_LIMIT_DEFAULT="1000 per minute",
        RATE_LIMIT_WRITE="200 per minute",
    )

    register_middleware(app)
    register_error_handlers(app)
    init_metrics(app)
    app.register_blueprint(metrics_bp)

    @app.get("/health")
    def health():
        return jsonify(status="ok", service=app.config["APP_NAME"])

    @app.get("/boom")
    def boom():
        raise RuntimeError("boom")

    @app.post("/echo")
    def echo():
        payload = request.get_json()
        return jsonify(payload or {}), 200

    return app


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client
