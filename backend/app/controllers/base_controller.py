from flask import current_app, g, jsonify, request

try:
    import sentry_sdk

    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False


class BaseController:
    def handle_success(self, data, status_code=200):
        return jsonify(data), status_code

    def require_json(self):
        """Return a 415 response tuple if Content-Type is not application/json, else None."""
        content_type = request.content_type or ""
        if "application/json" not in content_type:
            return jsonify(
                {
                    "error": "unsupported_media_type",
                    "message": "Content-Type must be application/json.",
                }
            ), 415
        return None

    def handle_error(self, error, operation_name):
        error_type = type(error).__name__
        msg = str(error)

        if SENTRY_AVAILABLE and current_app.config.get("SENTRY_DSN"):
            try:
                sentry_sdk.set_tag("operation", operation_name)
                sentry_sdk.capture_exception(error)
            except Exception:
                pass

        # Pydantic validation error - check first before string comparison
        if hasattr(error, "errors"):
            # Convert Pydantic errors to JSON-serializable format
            details = []
            for err in error.errors():
                detail = {
                    "loc": list(err.get("loc", [])),
                    "msg": err.get("msg", ""),
                    "type": err.get("type", ""),
                }
                if "input" in err:
                    detail["input"] = str(err["input"])
                details.append(detail)
            return jsonify(
                {"error": "validation_error", "message": msg, "details": details}
            ), 422

        # We'll map some known exceptions to nice JSON responses
        if error_type == "ValidationError":
            return jsonify({"error": "validation_error", "message": msg}), 400
        elif error_type == "ConflictError" or error_type == "IntegrityError":
            return jsonify({"error": "conflict", "message": msg}), 409
        elif error_type == "NotFoundError":
            return jsonify({"error": "not_found", "message": msg}), 404
        elif error_type == "ForbiddenError":
            return jsonify({"error": "forbidden", "message": msg}), 403
        elif error_type == "GoneError":
            return jsonify({"error": "gone", "message": msg}), 410
        elif error_type == "ValueError":
            if "not found" in msg.lower():
                return jsonify({"error": "not_found", "message": msg}), 404
            return jsonify({"error": "bad_request", "message": msg}), 400

        current_app.logger.exception(
            "Unexpected error in %s: %s", operation_name, error
        )

        payload = {"status": "error", "message": "An internal server error occurred."}
        if current_app.config.get("EXPOSE_ERROR_DETAILS"):
            payload["error_type"] = error_type
            payload["error_detail"] = msg
            payload["operation"] = operation_name
            payload["request_id"] = getattr(g, "request_id", None)

        return jsonify(payload), 500
