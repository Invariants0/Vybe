from flask import Blueprint, current_app, request

from backend.app.controllers.url_controller import UrlController
from backend.app.services.url_service import UrlService

urls_bp = Blueprint("urls_bp", __name__, url_prefix="/urls")


def get_controller():
    # Cache on the app object so we instantiate exactly ONCE per gunicorn worker,
    # not once per request.  At 500 VUs this eliminates ~15k allocs/sec.
    app = current_app._get_current_object()
    ctrl = getattr(app, "_url_controller", None)
    if ctrl is None:
        ctrl = UrlController(UrlService(app.config))
        ctrl.set_config(app.config)
        app._url_controller = ctrl
    return ctrl


@urls_bp.post("")
def create_url():
    return get_controller().create_url(request)

@urls_bp.get("")
def list_urls():
    return get_controller().list_urls(request)

@urls_bp.get("/<int:url_id>")
def get_url(url_id):
    return get_controller().get_url(url_id)

@urls_bp.put("/<int:url_id>")
def update_url(url_id):
    return get_controller().update_url(url_id, request)

@urls_bp.delete("/<int:url_id>")
def delete_url(url_id):
    return get_controller().delete_url(url_id)
