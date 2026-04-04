import logging

from flask import current_app, g, jsonify

try:
    import sentry_sdk
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False


class BaseController:
    def handle_success(self, data, status_code=200):
        return jsonify(data), status_code

    def handle_error(self, error, operation_name):
        error_type = type(error).__name__
        msg = str(error)

        if SENTRY_AVAILABLE and current_app.config.get("SENTRY_DSN"):
            with sentry_sdk.push_scope() as scope:
                scope.set_tag("operation", operation_name)
                sentry_sdk.capture_exception(error)

        # We'll map some known exceptions to nice JSON responses
        if error_type == "ValidationError":
            return jsonify({"error": "validation_error", "message": msg}), 422
        elif error_type == "ConflictError" or error_type == "IntegrityError":
            return jsonify({"error": "conflict", "message": msg}), 409
        elif error_type == "NotFoundError" or error_type == "ValueError":
            return jsonify({"error": "not_found", "message": msg}), 404
        
        # Pydantic validation error string mapping
        if hasattr(error, "errors"):
            return jsonify({"error": "validation_error", "message": "Invalid schema data", "details": error.errors()}), 422

        logging.exception(f"Unexpected error in {operation_name}: {error}")
        return jsonify({"error": "internal_error", "message": "An unexpected error occurred"}), 500
