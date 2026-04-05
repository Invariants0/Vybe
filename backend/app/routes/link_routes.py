from flask import Blueprint, current_app, jsonify, redirect

from backend.app.config.errors import ForbiddenError, NotFoundError
from backend.app.services.url_service import UrlService

links_bp = Blueprint("links", __name__)


def _get_service():
    app = current_app._get_current_object()
    svc = getattr(app, "_link_url_service", None)
    if svc is None:
        svc = UrlService(app.config)
        app._link_url_service = svc
    return svc


@links_bp.get("/<string:code>")
def follow_short_link(code):
    try:
        destination = _get_service().resolve_redirect(code)
    except ForbiddenError:
        return jsonify(
            {"error": "gone", "message": "This link has been deactivated."}
        ), 410
    except NotFoundError:
        return jsonify(
            {"error": "not_found", "message": "Link not found."}
        ), 404

    if not destination:
        return jsonify(
            {"error": "not_found", "message": "Link not found or inactive"}
        ), 404

    return redirect(
        destination, code=current_app.config["DEFAULT_REDIRECT_STATUS_CODE"]
    )
