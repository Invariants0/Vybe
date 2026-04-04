from __future__ import annotations

from typing import Any, Optional
import os

try:
    import redis
except Exception:  # pragma: no cover - redis is optional at runtime
    redis = None

_client: Optional["redis.Redis"] = None


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


def get_client(config: Optional[dict[str, Any]] = None) -> Optional["redis.Redis"]:
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
            socket_timeout=0.2,
            socket_connect_timeout=0.2,
        )
        return _client
    except Exception:
        return None


def cache_get(key: str, config: Optional[dict[str, Any]] = None) -> Optional[str]:
    client = get_client(config)
    if not client:
        return None
    try:
        return client.get(key)
    except Exception:
        return None


def cache_set(key: str, value: str, ttl_seconds: int, config: Optional[dict[str, Any]] = None) -> bool:
    client = get_client(config)
    if not client:
        return False
    try:
        client.setex(key, ttl_seconds, value)
        return True
    except Exception:
        return False
