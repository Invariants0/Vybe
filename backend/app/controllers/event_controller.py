from backend.app.controllers.base_controller import BaseController


class EventController(BaseController):
    def __init__(self, event_service):
        self.event_service = event_service

    def list_events(self, request):
        try:
            url_id = request.args.get("url_id", type=int)
            page = request.args.get("page", 1, type=int)
            per_page = request.args.get("per_page", 50, type=int)
            
            events = self.event_service.list_events(url_id=url_id, page=page, per_page=per_page)
            return self.handle_success([self.event_service.serialize_event(e) for e in events])
        except Exception as e:
            return self.handle_error(e, "list_events")
