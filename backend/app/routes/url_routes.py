from flask import Blueprint, current_app, request

from backend.app.controllers.url_controller import UrlController
from backend.app.services.url_service import UrlService

urls_bp = Blueprint("urls_bp", __name__, url_prefix="/urls")

def get_controller():
    controller = UrlController(UrlService(current_app.config))
    controller.set_config(current_app.config)
    return controller


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
