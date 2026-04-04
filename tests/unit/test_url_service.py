"""Unit tests for UrlService."""
import json
import pytest
from unittest.mock import MagicMock, patch
from backend.app.services.url_service import UrlService
from backend.app.models.url_model import ShortURL
from backend.app.models.user_model import User


@pytest.fixture
def service():
    url_repo = MagicMock()
    user_repo = MagicMock()
    event_repo = MagicMock()
    svc = UrlService(
        config={},
        url_repo=url_repo,
        user_repo=user_repo,
        event_repo=event_repo,
    )
    return svc, url_repo, user_repo, event_repo


# ---------------------------------------------------------------------------
# create_url
# ---------------------------------------------------------------------------

def test_create_url_user_not_found(service):
    """Bronze Tier: Fail if user doesn't exist."""
    svc, url_repo, user_repo, event_repo = service
    user_repo.get_by_id.return_value = None

    with pytest.raises(ValueError, match="User with id 999 does not exist."):
        svc.create_url(user_id=999, original_url="https://google.com", title="Google")


def test_create_url_success(service):
    """Bronze Tier: Successfully create URL and log event."""
    svc, url_repo, user_repo, event_repo = service

    mock_user = MagicMock(spec=User)
    mock_user.id = 1
    user_repo.get_by_id.return_value = mock_user

    mock_url = MagicMock(spec=ShortURL)
    mock_url.id = 1
    mock_url.short_code = "abc123"
    mock_url.original_url = "https://google.com"
    mock_url.user_id_id = 1
    url_repo.create.return_value = mock_url
    url_repo.find_by_code.return_value = None  # unique code

    # Patch cache_set so the test doesn't need a Redis server
    with patch("backend.app.services.url_service.cache_set"):
        result = svc.create_url(user_id=1, original_url="https://google.com", title="Google")

    assert result == mock_url
    event_repo.log_event.assert_called_once_with(mock_url, "created", user=mock_user)


# ---------------------------------------------------------------------------
# resolve_redirect — DB path (cache miss)
# ---------------------------------------------------------------------------

def test_resolve_redirect_success_db_path(service):
    """Bronze Tier: Resolve valid short code (no cache) and log access event."""
    svc, url_repo, user_repo, event_repo = service

    mock_url = MagicMock(spec=ShortURL)
    mock_url.id = 1
    mock_url.short_code = "xyz"
    mock_url.original_url = "https://github.com"
    mock_url.is_active = True
    mock_url.user_id_id = None
    url_repo.find_by_code.return_value = mock_url

    with patch("backend.app.services.url_service.cache_get", return_value=None), \
         patch("backend.app.services.url_service.cache_set"):
        result = svc.resolve_redirect("xyz")

    assert result == "https://github.com"
    event_repo.log_event.assert_called_once_with(mock_url, "accessed")


# ---------------------------------------------------------------------------
# resolve_redirect — cache hit path
# ---------------------------------------------------------------------------

def test_resolve_redirect_success_cache_hit(service):
    """Gold Tier: Cache hit should return URL and still log the access event."""
    svc, url_repo, user_repo, event_repo = service

    cached_payload = json.dumps({"id": 42, "original_url": "https://cached.com", "user_id": 7})

    with patch("backend.app.services.url_service.cache_get", return_value=cached_payload):
        result = svc.resolve_redirect("cached_code")

    assert result == "https://cached.com"
    # Event must still be logged even on a cache hit — the P0 bug must stay fixed
    event_repo.log_event.assert_called_once()
    # DB must NOT be queried at all on cache hit
    url_repo.find_by_code.assert_not_called()


# ---------------------------------------------------------------------------
# resolve_redirect — inactive / not found
# ---------------------------------------------------------------------------

def test_resolve_redirect_inactive(service):
    """Bronze Tier: Return None for inactive URLs."""
    svc, url_repo, user_repo, event_repo = service

    mock_url = MagicMock(spec=ShortURL)
    mock_url.id = 1
    mock_url.short_code = "xyz"
    mock_url.is_active = False
    url_repo.find_by_code.return_value = mock_url

    with patch("backend.app.services.url_service.cache_get", return_value=None):
        result = svc.resolve_redirect("xyz")

    assert result is None
    event_repo.log_event.assert_not_called()


def test_resolve_redirect_not_found(service):
    """Return None when short code doesn't exist in DB."""
    svc, url_repo, user_repo, event_repo = service
    url_repo.find_by_code.return_value = None

    with patch("backend.app.services.url_service.cache_get", return_value=None):
        result = svc.resolve_redirect("missing")

    assert result is None
    event_repo.log_event.assert_not_called()


# ---------------------------------------------------------------------------
# resolve_redirect — corrupt cache
# ---------------------------------------------------------------------------

def test_resolve_redirect_corrupt_cache_falls_back_to_db(service):
    """Corrupt cache entry should be evicted and DB path used as fallback."""
    svc, url_repo, user_repo, event_repo = service

    mock_url = MagicMock(spec=ShortURL)
    mock_url.id = 5
    mock_url.short_code = "bad"
    mock_url.original_url = "https://fallback.com"
    mock_url.is_active = True
    mock_url.user_id_id = None
    url_repo.find_by_code.return_value = mock_url

    with patch("backend.app.services.url_service.cache_get", return_value="NOT_VALID_JSON"), \
         patch("backend.app.services.url_service.cache_delete") as mock_del, \
         patch("backend.app.services.url_service.cache_set"):
        result = svc.resolve_redirect("bad")

    assert result == "https://fallback.com"
    mock_del.assert_called_once_with("shorturl:bad", {})
    event_repo.log_event.assert_called_once_with(mock_url, "accessed")


# ---------------------------------------------------------------------------
# update_url — cache invalidation
# ---------------------------------------------------------------------------

def test_update_url_evicts_cache(service):
    """P1 fix: Updating a URL must evict its cache entry immediately."""
    svc, url_repo, user_repo, event_repo = service

    mock_url = MagicMock(spec=ShortURL)
    mock_url.short_code = "evict_me"
    url_repo.update.return_value = mock_url

    with patch("backend.app.services.url_service.cache_delete") as mock_del:
        svc.update_url(1, {"is_active": False})

    mock_del.assert_called_once_with("shorturl:evict_me", {})


def test_update_url_no_changes_skips_cache(service):
    """update_url with empty data must not attempt any cache eviction."""
    svc, url_repo, user_repo, event_repo = service

    mock_url = MagicMock(spec=ShortURL)
    url_repo.get_by_id.return_value = mock_url

    with patch("backend.app.services.url_service.cache_delete") as mock_del:
        result = svc.update_url(1, {})

    mock_del.assert_not_called()
    assert result == mock_url
