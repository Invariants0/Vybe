import json
from typing import Any, Dict, List, Optional

from backend.app.models import Event
from backend.app.repositories.event_repository import EventRepository


class EventService:
    def __init__(self, config: Optional[Dict[str, Any]] = None, repo: Optional[EventRepository] = None):
        self.config = config or {}
        self.repo = repo or EventRepository()

    def list_events(self, url_id: Optional[int] = None, page: int = 1, per_page: int = 50) -> List[Event]:
        """List all events, optionally filtered by url_id."""
        skip = (page - 1) * per_page
        if url_id:
            return self.repo.list_for_url(url_id, skip=skip, limit=per_page)
        return self.repo.get_all(skip=skip, limit=per_page, order_by=Event.id)

    @staticmethod
    def serialize_event(event: Event) -> Dict[str, Any]:
        """Convert Event model to API-friendly dictionary."""
        return {
            "id": event.id,
            "short_url_id": event.url_id.id,
            "user_id": event.user_id.id if event.user_id else None,
            "event_type": event.event_type,
            "timestamp": event.timestamp.isoformat(),
            "details": event.get_details()
        }
