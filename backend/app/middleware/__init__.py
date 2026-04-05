import logging
import time
import uuid

from flask import g, has_request_context, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

try:
    import sentry_sdk

    _SENTRY_AVAILABLE = True
except ImportError:
    sentry_sdk = None  # type: ignore[assignment]
    _SENTRY_AVAILABLE = False

AUTH_EXEMPT_ENDPOINTS = {
    "health",
    "readiness",
    "metrics.metrics",
    "links.follow_short_link",
    "static",
}


def _rate_limit_key() -> str:
    if has_request_context():
        auth_subject = getattr(g, "auth_subject", None)
        if auth_subject:
            return str(auth_subject)
    return get_remote_address()


limiter = Limiter(
    key_func=_rate_limit_key,
    default_limits=[],
    storage_uri="memory://",
)


def _configured_tokens(app) -> set[str]:
    tokens = set()
    single = app.config.get("API_AUTH_TOKEN")
    if single:
        tokens.add(str(single).strip())
    many = app.config.get("API_AUTH_TOKENS", "")
    if isinstance(many, str):
        tokens.update(token.strip() for token in many.split(",") if token.strip())
    return tokens


def _extract_auth_token() -> str | None:
    auth_header = request.headers.get("Authorization", "")
    if auth_header.lower().startswith("bearer "):
        return auth_header[7:].strip()
    token = request.headers.get("X-API-Token")
    if token:
        return token.strip()
    return None


def register_middleware(app):
    import json

    class JsonFormatter(logging.Formatter):
        def format(self, record):
            log_record = {
                "timestamp": self.formatTime(record, self.datefmt),
                "level": record.levelname,
                "name": record.name,
                "request_id": getattr(record, "request_id", "-"),
                "message": record.getMessage(),
            }
            if record.exc_info:
                log_record["exc_info"] = self.formatException(record.exc_info)
            return json.dumps(log_record)

    root_logger = logging.getLogger()
    root_logger.setLevel(
        getattr(logging, app.config["LOG_LEVEL"].upper(), logging.INFO)
    )

    if not root_logger.handlers:
        handler = logging.StreamHandler()
        root_logger.addHandler(handler)

    class RequestIdFilter(logging.Filter):
        def filter(self, record):
            if has_request_context():
                record.request_id = getattr(g, "request_id", "-")
            else:
                record.request_id = "-"
            return True

    for handler in root_logger.handlers:
        handler.setFormatter(JsonFormatter())
        handler.addFilter(RequestIdFilter())

    limiter._storage_uri = app.config.get("RATE_LIMIT_STORAGE_URI", "memory://")
    limiter.enabled = bool(app.config.get("RATE_LIMIT_ENABLED", True))
    limiter.init_app(app)

    @app.before_request
    def _attach_request_context():
        g.request_id = request.headers.get("X-Request-Id", str(uuid.uuid4()))
        g.request_started_at = time.perf_counter()

        # Add request context to Sentry (SDK v2 compatible)
        if _SENTRY_AVAILABLE:
            try:
                sentry_sdk.set_tag("request_id", g.request_id)
                sentry_sdk.set_context(
                    "request",
                    {
                        "method": request.method,
                        "url": request.url,
                    },
                )
            except Exception:
                pass

    @app.before_request
    def _authenticate_request():
        if not app.config.get("AUTH_ENABLED"):
            g.auth_subject = None
            return None

        if request.endpoint in AUTH_EXEMPT_ENDPOINTS:
            g.auth_subject = "anonymous"
            return None

        valid_tokens = _configured_tokens(app)
        presented_token = _extract_auth_token()
        if presented_token and presented_token in valid_tokens:
            g.auth_subject = presented_token
            return None

        app.logger.warning(
            "Unauthorized request rejected for endpoint=%s",
            request.endpoint or request.path,
        )
        return jsonify(
            {"error": "unauthorized", "message": "A valid API token is required."}
        ), 401

    @app.after_request
    def _log_response(response):
        # Only log if request_started_at was set (may not be in some test scenarios)
        if hasattr(g, "request_started_at"):
            duration_ms = round((time.perf_counter() - g.request_started_at) * 1000, 2)
            response.headers["X-Request-Id"] = g.request_id

            # Enhanced logging with status code
            log_message = f"{request.method} {request.path} -> {response.status_code} ({duration_ms}ms)"

            if response.status_code >= 500:
                app.logger.error(log_message)
            elif response.status_code >= 400:
                app.logger.warning(log_message)
            else:
                app.logger.info(log_message)

        return response
