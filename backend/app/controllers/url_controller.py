import json

from backend.app.controllers.base_controller import BaseController
from backend.app.validators.schemas import CreateUrlSchema, UpdateUrlSchema
from backend.app.utils.cache import cache_get, cache_set, cache_delete


class UrlController(BaseController):
    def __init__(self, url_service):
        self.url_service = url_service
        self.config = None  # Will be set if passed in

    def set_config(self, config):
        """Set config for cache operations."""
        self.config = config

    def create_url(self, request):
        try:
            err = self.require_json()
            if err:
                return err

            idempotency_key = request.headers.get("Idempotency-Key")
            if idempotency_key:
                cache_key = f"idempotency:url:{idempotency_key}"
                cached_resp = cache_get(cache_key, self.config)
                if cached_resp:
                    return self.handle_success(json.loads(cached_resp), 201)

            data = request.get_json()
            if not data:
                raise ValueError("Payload cannot be empty")

            schema = CreateUrlSchema(**data)
            url = self.url_service.create_url(
                user_id=schema.user_id,
                original_url=str(schema.original_url),
                title=schema.title,
            )

            result = {
                "id": url.id,
                "user_id": url.user_id.id,
                "short_code": url.short_code,
                "original_url": url.original_url,
                "title": url.title,
                "is_active": url.is_active,
                "created_at": url.created_at.isoformat(),
                "updated_at": url.updated_at.isoformat(),
            }

            if idempotency_key:
                # Cache the successful payload against the idempotency key for 24h
                cache_set(
                    f"idempotency:url:{idempotency_key}",
                    json.dumps(result),
                    86400,
                    self.config,
                )

            return self.handle_success(result, 201)
        except Exception as e:
            return self.handle_error(e, "create_url")

    def list_urls(self, request):
        try:
            user_id = request.args.get("user_id", type=int)
            is_active_raw = request.args.get("is_active")
            is_active = None
            if is_active_raw is not None:
                is_active = is_active_raw.lower() == "true"

            # Create cache key based on user_id filter
            cache_key = f"urls:list:{user_id or 'all'}:{is_active}"

            # Try to get from cache
            cached = cache_get(cache_key, self.config)
            if cached:
                return self.handle_success(json.loads(cached))

            # Cache miss - fetch from DB
            urls = self.url_service.list_urls(user_id=user_id, is_active=is_active)
            result = [
                {
                    "id": u.id,
                    "user_id": u.user_id.id,
                    "short_code": u.short_code,
                    "original_url": u.original_url,
                    "title": u.title,
                    "is_active": u.is_active,
                    "created_at": u.created_at.isoformat(),
                    "updated_at": u.updated_at.isoformat(),
                }
                for u in urls
            ]

            # Short TTL (30s) for list caches.  At high write rates, wildcard
            # cache invalidation causes thrashing (writes nuke the cache faster
            # than reads can benefit from it).  A 30s eventual-consistency window
            # is acceptable and keeps list reads off Postgres.
            cache_set(cache_key, json.dumps(result), 30, self.config)

            return self.handle_success(result)
        except Exception as e:
            return self.handle_error(e, "list_urls")

    def get_url(self, url_id: int):
        try:
            cache_key = f"url:{url_id}"

            # Try to get from cache
            cached = cache_get(cache_key, self.config)
            if cached:
                return self.handle_success(json.loads(cached))

            # Cache miss - fetch from DB
            url = self.url_service.get_url(url_id)
            if not url:
                raise ValueError("URL not found")

            result = {
                "id": url.id,
                "user_id": url.user_id.id,
                "short_code": url.short_code,
                "original_url": url.original_url,
                "title": url.title,
                "is_active": url.is_active,
                "created_at": url.created_at.isoformat(),
                "updated_at": url.updated_at.isoformat(),
            }

            # Store in cache for 5 minutes
            cache_set(cache_key, json.dumps(result), 300, self.config)

            return self.handle_success(result)
        except Exception as e:
            return self.handle_error(e, "get_url")

    def update_url(self, url_id: int, request):
        try:
            data = request.get_json() or {}
            schema = UpdateUrlSchema(**data)

            updates = schema.model_dump(exclude_unset=True)
            url = self.url_service.update_url(url_id, updates)
            if not url:
                raise ValueError("URL not found")

            # Invalidate only the exact key for this URL.
            # The service layer already handles shorturl:<code> eviction.
            # We do NOT scan-delete urls:list:* — see create_url comment.
            cache_delete(f"url:{url_id}", self.config)

            return self.handle_success(
                {
                    "id": url.id,
                    "user_id": url.user_id.id,
                    "short_code": url.short_code,
                    "original_url": url.original_url,
                    "title": url.title,
                    "is_active": url.is_active,
                    "created_at": url.created_at.isoformat(),
                    "updated_at": url.updated_at.isoformat(),
                }
            )
        except Exception as e:
            return self.handle_error(e, "update_url")

    def delete_url(self, url_id: int):
        try:
            url = self.url_service.get_url(url_id)
            if url:
                self.url_service.delete_url(url_id)
                cache_delete(f"url:{url_id}", self.config)
            return self.handle_success({}, 204)
        except Exception as e:
            return self.handle_error(e, "delete_url")
