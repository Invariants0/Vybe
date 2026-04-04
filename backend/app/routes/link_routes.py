from flask import Blueprint, current_app, jsonify, redirect, request

from backend.app.services.url_service import UrlService

links_bp = Blueprint("links", __name__)


@links_bp.get("/<string:code>")
def follow_short_link(code):
    service = UrlService(current_app.config)
    destination = service.resolve_redirect(code)
    if not destination:
        return jsonify({"error": "not_found", "message": "Link not found or inactive"}), 404
        
    return redirect(destination, code=current_app.config["DEFAULT_REDIRECT_STATUS_CODE"])
