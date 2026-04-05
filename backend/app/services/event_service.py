import json

from typing import Any, Dict, List, Optional

from backend.app.models import Event, ShortURL, User
from backend.app.repositories.event_repository import EventRepository


class EventService:
    def __init__(self, config: Optional[Dict[str, Any]] = None, repo: Optional[EventRepository] = None):
        self.config = config or {}
        self.repo = repo or EventRepository()

    def list_events(
        self,
        url_id: Optional[int] = None,
        user_id: Optional[int] = None,
        event_type: Optional[str] = None,
        page: int = 1,
        per_page: int = 50
    ) -> List[Event]:
        skip = (page - 1) * per_page
        return self.repo.list_filtered(
            url_id=url_id,
            user_id=user_id,
            event_type=event_type,
            skip=skip,
            limit=per_page
        )

    def create_event(
        self,
        url_id: int,
        event_type: str,
        user_id: Optional[int] = None,
        details: Optional[Dict] = None
    ) -> Event:
        if not url_id:
            raise ValueError("url_id is required")
        if not event_type:
            raise ValueError("event_type is required")

        short_url = ShortURL.get_or_none(ShortURL.id == url_id)
        if not short_url:
            raise ValueError(f"URL with id {url_id} does not exist")

        details_str = json.dumps(details or {
            "short_code": short_url.short_code,
            "original_url": short_url.original_url,
        })
        return self.repo.create(
            url_id=url_id,
            user_id=user_id,
            event_type=event_type,
            details=details_str,
        )

    @staticmethod
    def serialize_event(event: Event) -> Dict[str, Any]:
        return {
            "id": event.id,
            "url_id": event.url_id.id,
            "short_url_id": event.url_id.id,
            "user_id": event.user_id.id if event.user_id else None,
            "event_type": event.event_type,
            "timestamp": event.timestamp.isoformat(),
            "details": event.get_details()
        }
