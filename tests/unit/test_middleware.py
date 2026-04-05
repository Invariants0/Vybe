from __future__ import annotations

import json
import logging
from io import StringIO
from unittest.mock import patch

from flask import jsonify

from backend.app.middleware import limiter


def test_request_id_is_propagated_from_header(client):
    response = client.get("/health", headers={"X-Request-Id": "req-123"})

    assert response.status_code == 200
    assert response.headers["X-Request-Id"] == "req-123"


def test_structured_logging_includes_request_id_and_status(app):
    stream = StringIO()
    root_logger = logging.getLogger()
    template_handler = next(handler for handler in root_logger.handlers if getattr(handler, "formatter", None) is not None)
    handler = logging.StreamHandler(stream)
    handler.setFormatter(template_handler.formatter)
    for active_filter in template_handler.filters:
        handler.addFilter(active_filter)
    root_logger.addHandler(handler)

    try:
        with app.test_client() as client:
            response = client.get("/health", headers={"X-Request-Id": "req-456"})
    finally:
        root_logger.removeHandler(handler)

    assert response.status_code == 200
    log_line = stream.getvalue().strip().splitlines()[-1]
    payload = json.loads(log_line)
    assert payload["request_id"] == "req-456"
    assert "GET /health -> 200" in payload["message"]


def test_sentry_request_context_is_attached(app):
    with app.test_client() as client, patch("backend.app.middleware.sentry_sdk.set_tag") as set_tag, patch(
        "backend.app.middleware.sentry_sdk.set_context"
    ) as set_context:
        client.get("/health", headers={"X-Request-Id": "req-789"})

    set_tag.assert_any_call("request_id", "req-789")
    set_context.assert_called_once()


def test_authentication_blocks_protected_routes(app):
    app.config.update(AUTH_ENABLED=True, API_AUTH_TOKEN="secret-token")

    @app.get("/protected")
    def protected():
        return jsonify(ok=True)

    with app.test_client() as client:
        response = client.get("/protected")

    assert response.status_code == 401
    assert response.get_json()["error"] == "unauthorized"


def test_authentication_allows_valid_bearer_token(app):
    app.config.update(AUTH_ENABLED=True, API_AUTH_TOKEN="secret-token")

    @app.get("/protected-valid")
    def protected_valid():
        return jsonify(ok=True)

    with app.test_client() as client:
        response = client.get("/protected-valid", headers={"Authorization": "Bearer secret-token"})

    assert response.status_code == 200
    assert response.get_json() == {"ok": True}


def test_rate_limit_enforced_on_route(app):
    app.config["RATE_LIMIT_WRITE"] = "2 per minute"

    @app.get("/rate-limited")
    @limiter.limit("2 per minute")
    def rate_limited():
        return jsonify(ok=True)

    with app.test_client() as client:
        first = client.get("/rate-limited")
        second = client.get("/rate-limited")
        third = client.get("/rate-limited")

    assert first.status_code == 200
    assert second.status_code == 200
    assert third.status_code == 429
    assert third.get_json()["error"] == "rate_limited"
