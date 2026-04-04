from flask import Blueprint, current_app, request

from backend.app.controllers.event_controller import EventController
from backend.app.services.event_service import EventService

events_bp = Blueprint("events_bp", __name__, url_prefix="/events")

def get_controller():
    controller = EventController(EventService(current_app.config))
    controller.set_config(current_app.config)
    return controller

@events_bp.get("")
def list_events():
    return get_controller().list_events(request)
