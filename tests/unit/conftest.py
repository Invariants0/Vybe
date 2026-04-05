from __future__ import annotations

import pytest
from flask import Flask, jsonify, request

from backend.app.config.errors import register_error_handlers
from backend.app.middleware import register_middleware
from backend.app.routes.metrics_routes import init_metrics, metrics_bp
from backend.app.utils import cache
from backend.app.validators.schemas import CreateUserSchema
from pydantic import ValidationError


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

    @app.post("/users")
    def create_user():
        data = request.get_json()
        if data is None:
            return jsonify({"error": "bad_request", "message": "Invalid JSON"}), 400
        try:
            CreateUserSchema(**data)
            return jsonify(
                {"id": 1, "username": data.get("username"), "email": data.get("email")}
            ), 201
        except ValidationError as e:
            errors = [
                {
                    "loc": err.get("loc", []),
                    "msg": err.get("msg", ""),
                    "type": err.get("type", ""),
                }
                for err in e.errors()
            ]
            return jsonify({"error": "validation_error", "details": errors}), 422

    return app


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client
