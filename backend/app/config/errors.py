from flask import jsonify
from werkzeug.exceptions import BadRequest


class AppError(Exception):
    status_code = 400
    error_code = "app_error"

    def __init__(self, message, status_code=None, error_code=None):
        super().__init__(message)
        if status_code is not None:
            self.status_code = status_code
        if error_code is not None:
            self.error_code = error_code


class ValidationError(AppError):
    status_code = 400
    error_code = "validation_error"


class NotFoundError(AppError):
    status_code = 404
    error_code = "not_found"


class ConflictError(AppError):
    status_code = 409
    error_code = "conflict"


def register_error_handlers(app):
    @app.errorhandler(BadRequest)
    def _handle_bad_request(error):
        # Handle malformed JSON and other bad requests
        return jsonify({"error": "bad_request", "message": str(error)}), 400

    @app.errorhandler(AppError)
    def _handle_app_error(error):
        response = {
            "error": error.error_code,
            "message": str(error),
        }
        return jsonify(response), error.status_code

    @app.errorhandler(404)
    def _handle_404(_error):
        return jsonify(error="not_found", message="The requested resource was not found."), 404

    @app.errorhandler(405)
    def _handle_405(_error):
        return (
            jsonify(error="method_not_allowed", message="The requested HTTP method is not supported."),
            405,
        )

    @app.errorhandler(Exception)
    def _handle_unexpected_error(error):
        app.logger.exception("Unhandled exception: %s", error)
        return jsonify(status="error", message="An internal server error occurred."), 500
