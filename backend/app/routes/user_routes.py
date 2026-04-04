from flask import Blueprint, current_app, request

from backend.app.controllers.user_controller import UserController
from backend.app.services.user_service import UserService

users_bp = Blueprint("users_bp", __name__, url_prefix="/users")


def get_controller():
    app = current_app._get_current_object()
    ctrl = getattr(app, "_user_controller", None)
    if ctrl is None:
        ctrl = UserController(UserService(app.config))
        ctrl.set_config(app.config)
        app._user_controller = ctrl
    return ctrl


@users_bp.post("")
def create_user():
    return get_controller().create_user(request)

@users_bp.get("")
def list_users():
    return get_controller().list_users(request)

@users_bp.get("/<int:user_id>")
def get_user(user_id):
    return get_controller().get_user(user_id)

@users_bp.put("/<int:user_id>")
def update_user(user_id):
    return get_controller().update_user(user_id, request)

@users_bp.post("/bulk")
def bulk_import_users():
    return get_controller().bulk_import(request)
