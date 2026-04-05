from __future__ import annotations

import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from typing import Any, Optional

try:
    import redis
    from redis.backoff import NoBackoff
    from redis.retry import Retry
except Exception: 
    redis = None  # type: ignore[assignment]
    NoBackoff = None  # type: ignore[assignment]
    Retry = None  # type: ignore[assignment]

_client: Optional["redis.Redis"] = None  # type: ignore[type-arg]

logger = logging.getLogger(__name__)

def _sanitize_for_log(value: Any) -> Any:
    if isinstance(value, str):
        return value.replace("\r", "").replace("\n", "")
    return value


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


def _get_retry_attempts(config: Optional[dict[str, Any]] = None) -> int:
    if config and isinstance(config, dict):
        value = config.get("REDIS_RETRY_ATTEMPTS")
        if value is not None:
            return max(1, int(value))
    return max(1, int(os.getenv("REDIS_RETRY_ATTEMPTS", "3")))


def _get_retry_backoff(config: Optional[dict[str, Any]] = None) -> float:
    if config and isinstance(config, dict):
        value = config.get("REDIS_RETRY_BACKOFF_SECONDS")
        if value is not None:
            return max(0.0, float(value))
    return max(0.0, float(os.getenv("REDIS_RETRY_BACKOFF_SECONDS", "0.05")))


def _sleep_for_retry(attempt: int, config: Optional[dict[str, Any]] = None) -> None:
    backoff = _get_retry_backoff(config)
    if backoff > 0:
        time.sleep(backoff * attempt)


def _get_operation_timeout(config: Optional[dict[str, Any]] = None) -> float:
    if config and isinstance(config, dict):
        value = config.get("REDIS_OPERATION_TIMEOUT_SECONDS")
        if value is not None:
            return max(0.1, float(value))
    return max(0.1, float(os.getenv("REDIS_OPERATION_TIMEOUT_SECONDS", "0.75")))


def _execute_with_deadline(callback, config: Optional[dict[str, Any]] = None):
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(callback)
        return future.result(timeout=_get_operation_timeout(config))


def _with_retry(
    operation_name: str,
    key: str,
    callback,
    config: Optional[dict[str, Any]] = None,
):
    global _client

    attempts = _get_retry_attempts(config)
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            return _execute_with_deadline(callback, config)
        except FuturesTimeoutError:
            last_error = TimeoutError(f"Redis {operation_name} exceeded operation deadline")
            logger.warning(
                "Redis %s timed out for key=%s on attempt %s/%s",
                operation_name,
                _sanitize_for_log(key),
                attempt,
                attempts,
            )
        except Exception as e:
            last_error = e
            logger.warning(
                "Redis %s failed for key=%s on attempt %s/%s: %s",
                operation_name,
                _sanitize_for_log(key),
                attempt,
                attempts,
                e,
            )
            _client = None
            if attempt < attempts:
                _sleep_for_retry(attempt, config)

    if last_error is not None:
        logger.error("Redis %s exhausted retries for key=%s: %s", operation_name, _sanitize_for_log(key), last_error)
    return None


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

    def _build_client():
        nonlocal url
        client = redis.Redis.from_url(
            url,
            decode_responses=True,
            socket_timeout=0.5,
            socket_connect_timeout=0.5,
            max_connections=16,
            health_check_interval=5,
            retry_on_timeout=False,
            retry=Retry(NoBackoff(), 0) if Retry is not None and NoBackoff is not None else None,
        )
        client.ping()
        return client

    client = _with_retry("CONNECT", "redis:connect", _build_client, config)
    if not client:
        return None

    _client = client
    logger.info("Redis connection established: %s", url.split("@")[-1])
    return _client


def cache_get(key: str, config: Optional[dict[str, Any]] = None) -> Optional[str]:
    client = get_client(config)
    if not client:
        return None
    result = _with_retry("GET", key, lambda: client.get(key), config)
    return result if isinstance(result, str) or result is None else None


def cache_set(key: str, value: str, ttl_seconds: int, config: Optional[dict[str, Any]] = None) -> bool:
    client = get_client(config)
    if not client:
        return False
    result = _with_retry("SET", key, lambda: client.setex(key, ttl_seconds, value), config)
    return bool(result)


def cache_delete(key: str, config: Optional[dict[str, Any]] = None) -> bool:
    """Delete a cache key. Supports wildcard patterns (e.g., 'urls:list:*')."""
    client = get_client(config)
    if not client:
        return False
    try:
        if "*" in key:
            # For massive datasets, keys() is discouraged, but scan with default count=10 causes
            # thousands of blocking network round-trips to Redis, freezing Gunicorn workers.
            # Using scan_iter with chunky batches (count=5000) traverses safely without breaking the single-threaded event loops.
            deleted_count = 0
            batch = []

            def _delete_pattern() -> int:
                nonlocal deleted_count, batch
                for k in client.scan_iter(match=key, count=5000):
                    batch.append(k)
                    if len(batch) >= 500:
                        client.delete(*batch)
                        deleted_count += len(batch)
                        batch = []
                if batch:
                    client.delete(*batch)
                    deleted_count += len(batch)
                return deleted_count

            _with_retry("DELETE", key, _delete_pattern, config)
            logger.debug("Deleted %d keys matching pattern %s", deleted_count, key)
            return True
        else:
            return bool(_with_retry("DELETE", key, lambda: client.delete(key), config) is not None)
    except Exception as e:
        logger.error("Redis DELETE failed for key=%s: %s", _sanitize_for_log(key), e)
        return False
