import json
import logging
from collections import namedtuple
from typing import Any, Dict, List, Optional
import random

from peewee import IntegrityError

from backend.app.models import ShortURL
from backend.app.config.errors import ForbiddenError, NotFoundError
from backend.app.utils.codecs import generate_short_code
from backend.app.utils.cache import cache_get, cache_set, cache_delete
from backend.app.utils.urls import normalize_url

from backend.app.repositories.url_repository import UrlRepository
from backend.app.repositories.user_repository import UserRepository
from backend.app.repositories.event_repository import EventRepository

logger = logging.getLogger(__name__)

# Lightweight struct used on cache-hit path instead of creating a new class
# on every request (which allocates a Python type object + __dict__ descriptor
# per call — measurable GC pressure at thousands of req/s).
_UidProxy = namedtuple("_UidProxy", ["id"])
_CachedURL = namedtuple("_CachedURL", ["id", "short_code", "original_url", "user_id"])


class UrlService:
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        url_repo: Optional[UrlRepository] = None,
        user_repo: Optional[UserRepository] = None,
        event_repo: Optional[EventRepository] = None,
    ):
        self.config = config or {}
        self.short_code_length = self.config.get("DEFAULT_SHORT_CODE_LENGTH", 6)
        self.repo = url_repo or UrlRepository()
        self.user_repo = user_repo or UserRepository()
        self.event_repo = event_repo or EventRepository()

    def create_url(self, user_id: int, original_url: str, title: str) -> ShortURL:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with id {user_id} does not exist.")

        normalized_url = normalize_url(original_url)

        existing_urls = self.repo.get_all(
            user_id=user.id, original_url=normalized_url, is_active=True
        )
        if existing_urls:
            return existing_urls[0]

        short_url = None
        for _ in range(10):
            short_code = generate_short_code(self.short_code_length)
            try:
                short_url = self.repo.create(
                    user_id=user.id,
                    short_code=short_code,
                    original_url=normalized_url,
                    title=title,
                    is_active=True,
                )
                break
            except IntegrityError:
                continue

        if not short_url:
            raise IntegrityError(
                "Could not generate a unique short code after 10 attempts."
            )

        try:
            self.event_repo.log_event(short_url, "created", user=user)
        except Exception as e:
            logger.warning(
                "Failed to log creation event for short_url=%s: %s",
                short_url.short_code,
                e,
            )

        self._cache_short_url(short_url)
        return short_url

    def get_url(self, url_id: int) -> Optional[ShortURL]:
        return self.repo.get_by_id(url_id)

    def get_url_by_code(self, short_code: str) -> Optional[ShortURL]:
        return self.repo.find_by_code(short_code)

    def list_urls(
        self,
        user_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        per_page: int = 50,
    ) -> List[ShortURL]:
        filters = {}
        if user_id:
            filters["user_id"] = user_id
        if is_active is not None:
            filters["is_active"] = is_active
        skip = (page - 1) * per_page
        return self.repo.get_all(
            skip=skip, limit=per_page, order_by=ShortURL.id, **filters
        )

    def update_url(self, url_id: int, data: Dict[str, Any]) -> Optional[ShortURL]:
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

    def delete_url(self, url_id: int) -> None:
        url = self.repo.get_by_id(url_id)
        if url:
            cache_delete(f"shorturl:{url.short_code}", self.config)
        self.repo.delete(url_id)

    def resolve_redirect(self, short_code: str) -> Optional[str]:
        """
        Return the destination URL for a short code and record an 'accessed' event.

        Cache path (happy path):
            - Deserialise the JSON blob stored by _cache_short_url.
            - Build a lightweight namedtuple from the cached fields so the event
              logger never has to touch Postgres on a cache hit.
            - Log the event, then return the URL.

        DB fallback:
            - Used on first access or after a cache eviction.
            - Re-hydrates the cache entry for subsequent requests.
        """
        cached_raw = self._get_cached_raw(short_code)
        if cached_raw:
            try:
                data = json.loads(cached_raw)

                # Check active status from cache if present
                if not data.get("is_active", True):
                    raise ForbiddenError("URL has been deactivated.")

                uid = data.get("user_id")
                cached_url_obj = _CachedURL(
                    id=data["id"],
                    short_code=short_code,
                    original_url=data["original_url"],
                    user_id=_UidProxy(id=uid) if uid else None,
                )
                self._maybe_log_event(cached_url_obj)  # type: ignore[arg-type]
                return cached_url_obj.original_url
            except ForbiddenError:
                raise
            except Exception:
                logger.warning(
                    "Corrupt cache entry for short_code=%s, evicting.", short_code
                )
                cache_delete(f"shorturl:{short_code}", self.config)

        short_url = self.get_url_by_code(short_code)
        if not short_url:
            raise NotFoundError("URL not found.")

        if not short_url.is_active:
            # Cache the deactivated state to prevent DB hammers
            self._cache_short_url(short_url)
            raise ForbiddenError("URL has been deactivated.")

        self._maybe_log_event(short_url)
        self._cache_short_url(short_url)
        return short_url.original_url

    def _generate_unique_code(self) -> str:
        return generate_short_code(self.short_code_length)

    def _get_cached_raw(self, short_code: str) -> Optional[str]:
        return cache_get(f"shorturl:{short_code}", self.config)

    def _cache_short_url(self, url_obj: ShortURL) -> None:
        """
        Serialise the minimal URL fields needed by the cache path into Redis.

        We only ever cache: id, original_url, user_id (FK raw int).

        Peewee FK access note:
            ForeignKeyField stores the raw integer under `<field>_id` (i.e.
            `user_id_id` for a field named `user_id`). We prefer that attribute
            to avoid triggering a lazy SELECT on the related User row.
        """
        ttl = int(self.config.get("REDIS_DEFAULT_TTL_SECONDS", 300))
        cache_key = f"shorturl:{url_obj.short_code}"

        raw_uid: Optional[int] = getattr(url_obj, "user_id_id", None)
        if raw_uid is None:
            try:
                fk = object.__getattribute__(url_obj, "user_id")
                raw_uid = fk.id if fk is not None else None
            except Exception:
                raw_uid = None

        payload = json.dumps(
            {
                "id": url_obj.id,
                "original_url": url_obj.original_url,
                "user_id": raw_uid,
                "is_active": url_obj.is_active,
            }
        )
        cache_set(cache_key, payload, ttl, self.config)

    def _maybe_log_event(self, short_url: Any) -> None:
        """Probabilistically log an 'accessed' event based on EVENT_LOG_SAMPLE_RATE"""
        if not short_url:
            return
        sample_rate = float(self.config.get("EVENT_LOG_SAMPLE_RATE", 1.0))
        if sample_rate <= 0:
            return
        if sample_rate < 1.0 and random.random() > sample_rate:
            return
        try:
            self.event_repo.log_event(short_url, "accessed")
        except Exception as e:
            logger.warning(
                "Failed to log event for short_url=%s: %s",
                getattr(short_url, "short_code", "unknown"),
                e,
            )
