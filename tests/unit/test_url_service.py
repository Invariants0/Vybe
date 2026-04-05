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


def test_create_url_user_not_found(service):
    svc, url_repo, user_repo, event_repo = service
    user_repo.get_by_id.return_value = None

    with pytest.raises(ValueError, match="User with id 999 does not exist."):
        svc.create_url(user_id=999, original_url="https://google.com", title="Google")


def test_create_url_success(service):
    svc, url_repo, user_repo, event_repo = service

    mock_user = MagicMock(spec=User)
    mock_user.id = 1
    user_repo.get_by_id.return_value = mock_user

    mock_url = MagicMock(spec=ShortURL)
    mock_url.id = 1
    mock_url.short_code = "abc123"
    mock_url.original_url = "https://google.com"
    mock_url.user_id_id = 1
    mock_url.is_active = True
    url_repo.create.return_value = mock_url
    url_repo.find_by_code.return_value = None

    with patch("backend.app.services.url_service.cache_set"):
        result = svc.create_url(user_id=1, original_url="https://google.com", title="Google")

    assert result == mock_url
    event_repo.log_event.assert_called_once_with(mock_url, "created", user=mock_user)


def test_resolve_redirect_success_db_path(service):
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


def test_resolve_redirect_success_cache_hit(service):
    svc, url_repo, user_repo, event_repo = service
    cached_payload = json.dumps({"id": 42, "original_url": "https://cached.com", "user_id": 7})

    with patch("backend.app.services.url_service.cache_get", return_value=cached_payload):
        result = svc.resolve_redirect("cached_code")

    assert result == "https://cached.com"
    event_repo.log_event.assert_called_once()
    url_repo.find_by_code.assert_not_called()


def test_resolve_redirect_inactive(service):
    svc, url_repo, user_repo, event_repo = service

    mock_url = MagicMock(spec=ShortURL)
    mock_url.id = 1
    mock_url.short_code = "xyz"
    mock_url.original_url = "https://github.com"
    mock_url.is_active = False
    mock_url.user_id_id = None
    url_repo.find_by_code.return_value = mock_url

    with patch("backend.app.services.url_service.cache_get", return_value=None):
        with pytest.raises(Exception) as exc:
            svc.resolve_redirect("xyz")

    assert "deactivated" in str(exc.value).lower()
    event_repo.log_event.assert_not_called()


def test_resolve_redirect_not_found(service):
    svc, url_repo, user_repo, event_repo = service
    url_repo.find_by_code.return_value = None

    with patch("backend.app.services.url_service.cache_get", return_value=None):
        with pytest.raises(Exception) as exc:
            svc.resolve_redirect("missing")

    assert "not found" in str(exc.value).lower()
    event_repo.log_event.assert_not_called()


def test_resolve_redirect_corrupt_cache_falls_back_to_db(service):
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


def test_update_url_evicts_cache(service):
    svc, url_repo, user_repo, event_repo = service

    mock_url = MagicMock(spec=ShortURL)
    mock_url.short_code = "evict_me"
    url_repo.update.return_value = mock_url

    with patch("backend.app.services.url_service.cache_delete") as mock_del:
        svc.update_url(1, {"is_active": False})

    mock_del.assert_called_once_with("shorturl:evict_me", {})


def test_update_url_no_changes_skips_cache(service):
    svc, url_repo, user_repo, event_repo = service

    mock_url = MagicMock(spec=ShortURL)
    url_repo.get_by_id.return_value = mock_url

    with patch("backend.app.services.url_service.cache_delete") as mock_del:
        result = svc.update_url(1, {})

    mock_del.assert_not_called()
    assert result == mock_url
