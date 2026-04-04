from flask import Blueprint, current_app, redirect, request

from backend.app.services.url_shortener import URLShortenerService

redirect_bp = Blueprint("redirect", __name__)


@redirect_bp.get("/<string:code>")
def follow_short_link(code):
    service = URLShortenerService(current_app.config)
    destination = service.resolve_redirect(
        code=code,
        ip_address=request.headers.get("X-Forwarded-For", request.remote_addr),
        user_agent=request.user_agent.string,
        referer=request.referrer,
    )
    return redirect(destination, code=current_app.config["DEFAULT_REDIRECT_STATUS_CODE"])
