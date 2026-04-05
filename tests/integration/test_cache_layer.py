from __future__ import annotations

import time
from types import SimpleNamespace
from unittest.mock import MagicMock

from backend.app.services.url_service import UrlService
from backend.app.utils import cache


def test_cache_set_get_and_ttl_expiry(redis_config):
    assert cache.cache_set("cache:test:key", "value", 1, redis_config) is True
    assert cache.cache_get("cache:test:key", redis_config) == "value"

    time.sleep(1.2)

    assert cache.cache_get("cache:test:key", redis_config) is None


def test_cache_miss_falls_back_to_db_and_rehydrates(redis_config):
    url_repo = MagicMock()
    event_repo = MagicMock()
    user_repo = MagicMock()
    cached_url = SimpleNamespace(
        id=11,
        short_code="fallback",
        original_url="https://fallback.example.com",
        is_active=True,
        user_id_id=7,
        user_id=SimpleNamespace(id=7),
    )
    url_repo.find_by_code.return_value = cached_url
    service = UrlService(
        config={**redis_config, "EVENT_LOG_SAMPLE_RATE": 1.0},
        url_repo=url_repo,
        user_repo=user_repo,
        event_repo=event_repo,
    )

    assert cache.cache_get("shorturl:fallback", redis_config) is None

    destination = service.resolve_redirect("fallback")

    assert destination == "https://fallback.example.com"
    assert cache.cache_get("shorturl:fallback", redis_config) is not None
    event_repo.log_event.assert_called_once()


def test_cache_delete_supports_wildcard_patterns(redis_config):
    cache.cache_set("wildcard:1", "one", 10, redis_config)
    cache.cache_set("wildcard:2", "two", 10, redis_config)

    assert cache.cache_delete("wildcard:*", redis_config) is True
    assert cache.cache_get("wildcard:1", redis_config) is None
    assert cache.cache_get("wildcard:2", redis_config) is None


def test_redis_failure_returns_safe_defaults_and_service_falls_back():
    failing_config = {
        "REDIS_ENABLED": True,
        "REDIS_URL": "redis://localhost:6399/0",
        "REDIS_RETRY_ATTEMPTS": 2,
        "REDIS_RETRY_BACKOFF_SECONDS": 0.01,
    }

    url_repo = MagicMock()
    url_repo.find_by_code.return_value = SimpleNamespace(
        id=21,
        short_code="dbonly",
        original_url="https://db-only.example.com",
        is_active=True,
        user_id_id=3,
        user_id=SimpleNamespace(id=3),
    )
    service = UrlService(config=failing_config, url_repo=url_repo, user_repo=MagicMock(), event_repo=MagicMock())

    assert cache.cache_get("any-key", failing_config) is None
    assert cache.cache_set("any-key", "value", 1, failing_config) is False
    assert cache.cache_delete("any-key", failing_config) is False
    assert service.resolve_redirect("dbonly") == "https://db-only.example.com"
