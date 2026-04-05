import json
from typing import List

from backend.app.models import Event, ShortURL, User
from backend.app.repositories.base_repository import BaseRepository


class EventRepository(BaseRepository[Event]):
    def __init__(self):
        super().__init__(Event)

    def list_for_url(self, url_id: int, skip: int = 0, limit: int = 100) -> List[Event]:
        # List events for a URL with prefetched FKs to avoid N+1 queries
        from peewee import JOIN

        return list(
            Event.select(Event, ShortURL, User)
            .join(ShortURL, on=(Event.url_id == ShortURL.id))
            .switch(Event)
            .join(User, JOIN.LEFT_OUTER, on=(Event.user_id == User.id))
            .where(Event.url_id == url_id)
            .order_by(Event.id)
            .offset(skip)
            .limit(limit)
        )

    def list_filtered(
        self,
        url_id: int = None,
        user_id: int = None,
        event_type: str = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Event]:
        """List events with optional filters on url_id, user_id, and event_type."""
        from peewee import JOIN

        query = (
            Event.select(Event, ShortURL, User)
            .join(ShortURL, on=(Event.url_id == ShortURL.id))
            .switch(Event)
            .join(User, JOIN.LEFT_OUTER, on=(Event.user_id == User.id))
        )
        if url_id is not None:
            query = query.where(Event.url_id == url_id)
        if user_id is not None:
            query = query.where(Event.user_id == user_id)
        if event_type is not None:
            query = query.where(Event.event_type == event_type)
        return list(query.order_by(Event.id).offset(skip).limit(limit))

    def get_all(
        self, skip: int = 0, limit: int = 100, order_by=None, **filters
    ) -> List[Event]:
        """
        Override base get_all to prefetch FKs and avoid N+1 queries.

        Without the JOINs, serializing 50 events triggers 100 extra SELECTs
        (one for each event.url_id.id and event.user_id.id Peewee lazy-load).
        """
        from peewee import JOIN

        query = (
            Event.select(Event, ShortURL, User)
            .join(ShortURL, on=(Event.url_id == ShortURL.id))
            .switch(Event)
            .join(User, JOIN.LEFT_OUTER, on=(Event.user_id == User.id))
        )
        if order_by is not None:
            query = query.order_by(order_by)
        for key, value in filters.items():
            query = query.where(getattr(Event, key) == value)
        return list(query.offset(skip).limit(limit))

    def log_event(
        self, url: ShortURL, event_type: str, user: User | None = None
    ) -> Event:
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
