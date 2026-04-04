import logging
import time
import uuid

from flask import g, has_request_context, request


def register_middleware(app):
    logging.basicConfig(
        level=getattr(logging, app.config["LOG_LEVEL"].upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s request_id=%(request_id)s %(message)s",
    )

    class RequestIdFilter(logging.Filter):
        def filter(self, record):
            if has_request_context():
                record.request_id = getattr(g, "request_id", "-")
            else:
                record.request_id = "-"
            return True

    for handler in logging.getLogger().handlers:
        handler.addFilter(RequestIdFilter())

    @app.before_request
    def _attach_request_context():
        g.request_id = request.headers.get("X-Request-Id", str(uuid.uuid4()))
        g.request_started_at = time.perf_counter()

    @app.after_request
    def _log_response(response):
        duration_ms = round((time.perf_counter() - g.request_started_at) * 1000, 2)
        response.headers["X-Request-Id"] = g.request_id
        app.logger.info(
            "%s %s -> %s (%sms)",
            request.method,
            request.path,
            response.status_code,
            duration_ms,
        )
        return response
