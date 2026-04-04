from flask import Blueprint, current_app, jsonify, request

from backend.app.config import ValidationError
from backend.app.services.url_shortener import URLShortenerService

api_bp = Blueprint("api", __name__)


def _service():
    return URLShortenerService(current_app.config)


@api_bp.get("/healthz")
def api_health():
    return jsonify(status="ok")


@api_bp.post("/links")
def create_short_link():
    payload = request.get_json(silent=True) or {}
    short_url = _service().create_short_url(
        original_url=payload.get("url"),
        custom_alias=payload.get("custom_alias"),
        expires_at=payload.get("expires_at"),
        creator_ip=request.headers.get("X-Forwarded-For", request.remote_addr),
    )
    return jsonify(short_url), 201


@api_bp.get("/links/<string:code>")
def get_short_link(code):
    return jsonify(_service().get_short_url_stats(code))


@api_bp.get("/links/<string:code>/visits")
def get_short_link_visits(code):
    limit = request.args.get("limit", default=25, type=int)
    if limit < 1 or limit > 100:
        raise ValidationError("limit must be between 1 and 100.")
    return jsonify({"data": _service().get_recent_visits(code, limit=limit)})


@api_bp.patch("/links/<string:code>")
def update_short_link(code):
    payload = request.get_json(silent=True) or {}
    expires_at = payload.get("expires_at")
    if expires_at == "":
        expires_at = None
    elif expires_at is not None and not isinstance(expires_at, str):
        raise ValidationError("expires_at must be an ISO 8601 string or null.")
    is_active = payload.get("is_active")
    if is_active is not None and not isinstance(is_active, bool):
        raise ValidationError("is_active must be a boolean when provided.")

    return jsonify(_service().update_short_url(code, is_active=is_active, expires_at=expires_at))


@api_bp.delete("/links/<string:code>")
def delete_short_link(code):
    _service().deactivate_short_url(code)
    return "", 204
