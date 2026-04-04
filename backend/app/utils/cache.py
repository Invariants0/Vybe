from __future__ import annotations

import logging
import os
from typing import Any, Optional

try:
    import redis
except Exception:  # pragma: no cover - redis is optional at runtime
    redis = None  # type: ignore[assignment]

_client: Optional["redis.Redis"] = None  # type: ignore[type-arg]

logger = logging.getLogger(__name__)


def _is_enabled(config: Optional[dict[str, Any]] = None) -> bool:
    if config and isinstance(config, dict):
        val = config.get("REDIS_ENABLED")
        if isinstance(val, bool):
            return val
        if isinstance(val, str):
            return val.lower() == "true"
    return os.getenv("REDIS_ENABLED", "false").lower() == "true"


def _get_url(config: Optional[dict[str, Any]] = None) -> str:
    if config and isinstance(config, dict):
        val = config.get("REDIS_URL")
        if isinstance(val, str) and val:
            return val
    return os.getenv("REDIS_URL", "")


def get_client(config: Optional[dict[str, Any]] = None) -> Optional["redis.Redis"]:  # type: ignore[type-arg]
    global _client
    if _client is not None:
        return _client
    if not _is_enabled(config):
        return None
    if redis is None:
        return None
    url = _get_url(config)
    if not url:
        return None
    try:
        _client = redis.Redis.from_url(
            url,
            decode_responses=True,
            socket_timeout=0.5,
            socket_connect_timeout=0.5,
        )
        # Eagerly PING to catch misconfiguration at startup rather than silently
        # swallowing it on the first real request.
        _client.ping()
        logger.info("Redis connection established: %s", url.split("@")[-1])
        return _client
    except Exception as e:
        logger.error("Redis connection failed: %s", e, exc_info=True)
        _client = None  # Don't cache a broken client
        return None


def cache_get(key: str, config: Optional[dict[str, Any]] = None) -> Optional[str]:
    client = get_client(config)
    if not client:
        return None
    try:
        return client.get(key)
    except Exception as e:
        logger.error("Redis GET failed for key=%s: %s", key, e)
        return None


def cache_set(key: str, value: str, ttl_seconds: int, config: Optional[dict[str, Any]] = None) -> bool:
    client = get_client(config)
    if not client:
        return False
    try:
        client.setex(key, ttl_seconds, value)
        return True
    except Exception as e:
        logger.error("Redis SET failed for key=%s: %s", key, e)
        return False


def cache_delete(key: str, config: Optional[dict[str, Any]] = None) -> bool:
    """Delete a cache key. Supports wildcard patterns (e.g., 'urls:list:*')."""
    client = get_client(config)
    if not client:
        return False
    try:
        # If key contains wildcard, use SCAN to find and delete matching keys
        if "*" in key:
            cursor = 0
            deleted_count = 0
            while True:
                cursor, matched_keys = client.scan(cursor, match=key)
                if matched_keys:
                    client.delete(*matched_keys)
                    deleted_count += len(matched_keys)
                if cursor == 0:
                    break
            logger.debug("Deleted %d keys matching pattern %s", deleted_count, key)
            return True
        else:
            # Standard delete for non-wildcard keys
            client.delete(key)
            return True
    except Exception as e:
        logger.error("Redis DELETE failed for key=%s: %s", key, e)
        return False
