import json
from backend.app.controllers.base_controller import BaseController
from backend.app.utils.cache import cache_get, cache_set


class EventController(BaseController):
    def __init__(self, event_service):
        self.event_service = event_service
        self.config = None  # Will be set if passed in
    
    def set_config(self, config):
        """Set config for cache operations."""
        self.config = config

    def list_events(self, request):
        try:
            url_id = request.args.get("url_id", type=int)
            page = request.args.get("page", 1, type=int)
            per_page = request.args.get("per_page", 50, type=int)
            
            # Create cache key based on filters
            cache_key = f"events:list:{url_id or 'all'}:{page}:{per_page}"
            
            # Try to get from cache
            cached = cache_get(cache_key, self.config)
            if cached:
                return self.handle_success(json.loads(cached))
            
            # Cache miss - fetch from DB
            events = self.event_service.list_events(url_id=url_id, page=page, per_page=per_page)
            result = [self.event_service.serialize_event(e) for e in events]
            
            # Store in cache for 5 minutes
            cache_set(cache_key, json.dumps(result), 300, self.config)
            
            return self.handle_success(result)
        except Exception as e:
            return self.handle_error(e, "list_events")
