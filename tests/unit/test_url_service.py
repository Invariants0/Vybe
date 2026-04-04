import pytest
from unittest.mock import MagicMock
from backend.app.services.url_service import UrlService
from backend.app.models.url_model import ShortURL
from backend.app.models.user_model import User


@pytest.fixture
def service():
    # Mock repositories
    url_repo = MagicMock()
    user_repo = MagicMock()
    event_repo = MagicMock()
    
    # Initialize service with mocked dependencies
    service = UrlService(
        url_repo=url_repo,
        user_repo=user_repo,
        event_repo=event_repo
    )
    return service, url_repo, user_repo, event_repo


def test_create_url_user_not_found(service):
    """Bronze Tier: Fail if user doesn't exist."""
    svc, url_repo, user_repo, event_repo = service
    user_repo.get_by_id.return_value = None
    
    with pytest.raises(ValueError, match="User with id 999 does not exist."):
        svc.create_url(user_id=999, original_url="https://google.com", title="Google")


def test_create_url_success(service):
    """Bronze Tier: Successfully create URL and log event."""
    svc, url_repo, user_repo, event_repo = service
    
    # Setup mocks
    mock_user = User(id=1, username="testuser")
    user_repo.get_by_id.return_value = mock_user
    
    # Mock URL creation
    mock_url = ShortURL(id=1, short_code="abc123", original_url="https://google.com", user_id=mock_user)
    url_repo.create.return_value = mock_url
    url_repo.find_by_code.return_value = None  # Meaning code is unique
    
    result = svc.create_url(user_id=1, original_url="https://google.com", title="Google")
    
    assert result == mock_url
    # Verify event was logged via event_repo
    event_repo.log_event.assert_called_once_with(mock_url, "created", user=mock_user)


def test_resolve_redirect_success(service):
    """Bronze Tier: Resolve valid short code and log access event."""
    svc, url_repo, user_repo, event_repo = service
    
    mock_url = ShortURL(id=1, short_code="xyz", original_url="https://github.com", is_active=True)
    url_repo.find_by_code.return_value = mock_url
    
    result = svc.resolve_redirect("xyz")
    
    assert result == "https://github.com"
    event_repo.log_event.assert_called_once_with(mock_url, "accessed")


def test_resolve_redirect_inactive(service):
    """Bronze Tier: Return None for inactive URLs."""
    svc, url_repo, user_repo, event_repo = service
    
    mock_url = ShortURL(id=1, short_code="xyz", is_active=False)
    url_repo.find_by_code.return_value = mock_url
    
    result = svc.resolve_redirect("xyz")
    
    assert result is None
    event_repo.log_event.assert_not_called()
