from flask import Blueprint, current_app, request

from backend.app.controllers.event_controller import EventController
from backend.app.services.event_service import EventService

events_bp = Blueprint("events_bp", __name__, url_prefix="/events")


def get_controller():
    app = current_app._get_current_object()
    ctrl = getattr(app, "_event_controller", None)
    if ctrl is None:
        ctrl = EventController(EventService(app.config))
        ctrl.set_config(app.config)
        app._event_controller = ctrl
    return ctrl


@events_bp.get("")
def list_events():
    return get_controller().list_events(request)

@events_bp.post("")
def create_event():
    return get_controller().create_event(request)
