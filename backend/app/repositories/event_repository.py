import json
from typing import List

from backend.app.models import Event, ShortURL, User
from backend.app.repositories.base_repository import BaseRepository


class EventRepository(BaseRepository[Event]):
    def __init__(self):
        super().__init__(Event)

    def list_for_url(self, url_id: int, skip: int = 0, limit: int = 100) -> List[Event]:
        """List events for a URL with prefetched FKs to avoid N+1 queries."""
        return list(
            Event.select(Event, ShortURL, User)
            .join(ShortURL, on=(Event.url_id == ShortURL.id))
            .switch(Event)
            .join(User, on=(Event.user_id == User.id), join_type="LEFT OUTER")
            .where(Event.url_id == url_id)
            .order_by(Event.id)
            .offset(skip)
            .limit(limit)
        )

    def get_all(self, skip: int = 0, limit: int = 100, order_by=None, **filters) -> List[Event]:
        """Override base get_all to prefetch FKs and avoid N+1 queries.

        Without the JOINs, serializing 50 events triggers 100 extra SELECTs
        (one for each event.url_id.id and event.user_id.id Peewee lazy-load).
        """
        query = (
            Event.select(Event, ShortURL, User)
            .join(ShortURL, on=(Event.url_id == ShortURL.id))
            .switch(Event)
            .join(User, on=(Event.user_id == User.id), join_type="LEFT OUTER")
        )
        if order_by is not None:
            query = query.order_by(order_by)
        for key, value in filters.items():
            query = query.where(getattr(Event, key) == value)
        return list(query.offset(skip).limit(limit))

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
