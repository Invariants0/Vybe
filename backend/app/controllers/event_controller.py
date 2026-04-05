import json
from backend.app.controllers.base_controller import BaseController
from backend.app.utils.cache import cache_get, cache_set


class EventController(BaseController):
    def __init__(self, event_service):
        self.event_service = event_service
        self.config = None

    def set_config(self, config):
        self.config = config

    def list_events(self, request):
        try:
            url_id = request.args.get("url_id", type=int)
            user_id = request.args.get("user_id", type=int)
            event_type = request.args.get("event_type", type=str)
            page = request.args.get("page", 1, type=int)
            per_page = request.args.get("per_page", 50, type=int)

            # Create cache key based on filters
            cache_key = f"events:list:{url_id or 'all'}:{user_id or 'all'}:{event_type or 'all'}:{page}:{per_page}"

            # Try to get from cache
            cached = cache_get(cache_key, self.config)
            if cached:
                return self.handle_success(json.loads(cached))

            # Cache miss - fetch from DB
            events = self.event_service.list_events(
                url_id=url_id,
                user_id=user_id,
                event_type=event_type,
                page=page,
                per_page=per_page,
            )
            result = [self.event_service.serialize_event(e) for e in events]

            # Short TTL (30s)
            cache_set(cache_key, json.dumps(result), 30, self.config)

            return self.handle_success(result)
        except Exception as e:
            return self.handle_error(e, "list_events")

    def create_event(self, request):
        try:
            data = request.get_json()
            if not data:
                raise ValueError("Payload cannot be empty")

            details = data.get("details", {})
            if details is not None and not isinstance(details, dict):
                raise ValueError("details must be a JSON object")

            event = self.event_service.create_event(
                url_id=data.get("url_id"),
                user_id=data.get("user_id"),
                event_type=data.get("event_type"),
                details=details,
            )

            return self.handle_success(self.event_service.serialize_event(event), 201)
        except Exception as e:
            return self.handle_error(e, "create_event")
