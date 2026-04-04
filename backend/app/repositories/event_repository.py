import json
from typing import List

from backend.app.models import Event, ShortURL, User
from backend.app.repositories.base_repository import BaseRepository


class EventRepository(BaseRepository[Event]):
    def __init__(self):
        super().__init__(Event)

    def list_for_url(self, url_id: int, skip: int = 0, limit: int = 100) -> List[Event]:
        return self.get_all(skip=skip, limit=limit, order_by=Event.id, url_id=url_id)

    def log_event(self, url: ShortURL, event_type: str, user: User | None = None) -> Event:
        """Create an event with a JSON payload based on the URL."""
        details = json.dumps(
            {
                "short_code": url.short_code,
                "original_url": url.original_url,
            }
        )
        return self.create(
            url_id=url.id,
            user_id=user.id if user else (url.user_id.id if url.user_id else None),
            event_type=event_type,
            details=details,
        )
