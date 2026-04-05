import logging
import time
import uuid

from flask import g, has_request_context, request
import sentry_sdk


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
    root_logger.setLevel(getattr(logging, app.config["LOG_LEVEL"].upper(), logging.INFO))
    
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

    @app.before_request
    def _attach_request_context():
        g.request_id = request.headers.get("X-Request-Id", str(uuid.uuid4()))
        g.request_started_at = time.perf_counter()
        
        # Add request context to Sentry
        with sentry_sdk.configure_scope() as scope:
            scope.set_tag("request_id", g.request_id)
            scope.set_context("request", {
                "method": request.method,
                "url": request.url,
                "headers": dict(request.headers),
            })

    @app.after_request
    def _log_response(response):
        # Only log if request_started_at was set (may not be in some test scenarios)
        if hasattr(g, 'request_started_at'):
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
