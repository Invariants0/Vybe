import json
from typing import Any, Dict, List, Optional

from peewee import IntegrityError

from backend.app.models import Event, ShortURL, User
import random

from backend.app.utils.codecs import generate_short_code
from backend.app.utils.cache import cache_get, cache_set, cache_delete
from backend.app.utils.urls import normalize_url


from backend.app.repositories.url_repository import UrlRepository
from backend.app.repositories.user_repository import UserRepository
from backend.app.repositories.event_repository import EventRepository

class UrlService:
    def __init__(self, config: Optional[Dict[str, Any]] = None, url_repo: Optional[UrlRepository] = None, user_repo: Optional[UserRepository] = None, event_repo: Optional[EventRepository] = None):
        self.config = config or {}
        self.short_code_length = self.config.get("DEFAULT_SHORT_CODE_LENGTH", 6)
        self.repo = url_repo or UrlRepository()
        self.user_repo = user_repo or UserRepository()
        self.event_repo = event_repo or EventRepository()

    def create_url(self, user_id: int, original_url: str, title: str) -> ShortURL:
        """
        Create a new short URL for a user.
        Validates user exists, generates unique short_code, creates 'created' event.
        """
        # Ensure user exists
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with id {user_id} does not exist.")

        normalized_url = normalize_url(original_url)
        
        # Generate unique short code
        short_code = self._generate_unique_code()

        short_url = self.repo.create(
            user_id=user.id,
            short_code=short_code,
            original_url=normalized_url,
            title=title,
            is_active=True
        )

        # Log 'created' event
        self.event_repo.log_event(short_url, "created", user=user)
        self._cache_short_url(short_url.short_code, short_url)

        return short_url

    def get_url(self, url_id: int) -> Optional[ShortURL]:
        """Fetch URL by ID."""
        return self.repo.get_by_id(url_id)

    def get_url_by_code(self, short_code: str) -> Optional[ShortURL]:
        """Fetch URL by its short code."""
        return self.repo.find_by_code(short_code)

    def list_urls(self, user_id: Optional[int] = None) -> List[ShortURL]:
        """List all URLs, optionally filtered by user_id."""
        if user_id:
            return self.repo.list_for_user(user_id=user_id)
        return self.repo.get_all(order_by=ShortURL.id)

    def update_url(self, url_id: int, data: Dict[str, Any]) -> Optional[ShortURL]:
        """Update URL title or status."""
        updates = {}
        if "title" in data:
            updates["title"] = data["title"]
        if "is_active" in data:
            val = data["is_active"]
            if isinstance(val, str):
                updates["is_active"] = val.lower() == "true"
            else:
                updates["is_active"] = bool(val)

        if not updates:
            return self.get_url(url_id)

        obj = self.repo.update(url_id, **updates)
        if obj:
            cache_key = f"shorturl:{obj.short_code}"
            cache_delete(cache_key, self.config)
        return obj

    def resolve_redirect(self, short_code: str) -> Optional[str]:
        """
        Find destination URL and log 'accessed' event.
        Returns original_url if found and active, else None.
        """
        cached_data = self._get_cached_url(short_code)
        
        if cached_data:
            try:
                data = json.loads(cached_data)
                
                # Construct mock URL object to satisfy event logger without DB query
                class MockURL:
                    id = data["id"]
                    short_code = short_code
                    original_url = data["original_url"]
                    user_id = type('obj', (object,), {'id': data["user_id"]}) if data.get("user_id") else None

                mock_url = MockURL()
                
                # Log 'accessed' event
                self._maybe_log_event(mock_url)  # type: ignore

                return data["original_url"]
            except Exception:
                pass # Cache parsing failed, fallback to DB

        short_url = self.get_url_by_code(short_code)
        if not short_url or not short_url.is_active:
            return None

        # Log 'accessed' event
        self._maybe_log_event(short_url)

        self._cache_short_url(short_url.short_code, short_url)

        return short_url.original_url

    def _generate_unique_code(self) -> str:
        """Generate a unique short code."""
        for _ in range(10):  # Retry up to 10 times to avoid collisions
            code = generate_short_code(self.short_code_length)
            if not self.repo.find_by_code(code):
                return code
        raise IntegrityError("Could not generate a unique short code after 10 attempts.")

    def _get_cached_url(self, short_code: str) -> Optional[str]:
        cache_key = f"shorturl:{short_code}"
        return cache_get(cache_key, self.config)

    def _cache_short_url(self, short_code: str, url_obj: ShortURL) -> None:
        ttl = int(self.config.get("REDIS_DEFAULT_TTL_SECONDS", 300))
        cache_key = f"shorturl:{short_code}"
        
        # Try to safely extract user_id to prevent lazy Peewee loading
        uid = getattr(url_obj, 'user_id_id', None)
        if uid is None and url_obj.user_id:
            try:
                uid = url_obj.user_id.id
            except Exception:
                pass
                
        cache_data = json.dumps({
            "id": url_obj.id,
            "original_url": url_obj.original_url,
            "user_id": uid
        })
        cache_set(cache_key, cache_data, ttl, self.config)

    def _maybe_log_event(self, short_url: Optional[ShortURL]) -> None:
        if not short_url:
            return
        sample_rate = float(self.config.get("EVENT_LOG_SAMPLE_RATE", 1.0))
        if sample_rate <= 0:
            return
        if sample_rate < 1.0 and random.random() > sample_rate:
            return
        self.event_repo.log_event(short_url, "accessed")
