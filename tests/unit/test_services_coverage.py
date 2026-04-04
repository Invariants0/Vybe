"""Additional service tests for coverage."""
import pytest
from unittest.mock import Mock, MagicMock
from backend.app.services.user_service import UserService
from backend.app.services.url_service import UrlService
from backend.app.services.event_service import EventService
from backend.app.models.user_model import User
from backend.app.models.url_model import ShortURL
from backend.app.models.event_model import Event
from datetime import datetime


class TestUserServiceCoverage:
    """Additional user service tests."""
    
    def test_get_user_by_username_not_found(self):
        """Test getting user by username when not found."""
        user_repo = MagicMock()
        user_repo.find_by_username.return_value = None
        
        service = UserService(user_repo=user_repo)
        result = service.get_user_by_username("nonexistent")
        
        assert result is None
    
    def test_update_user_with_kwargs(self):
        """Test updating user with kwargs instead of dict."""
        user_repo = MagicMock()
        mock_user = User(id=1, username="updated", email="test@example.com")
        user_repo.update.return_value = mock_user
        
        service = UserService(user_repo=user_repo)
        result = service.update_user(1, username="updated")
        
        assert result == mock_user
        user_repo.update.assert_called_once()
    
    def test_update_user_no_changes(self):
        """Test updating user with no actual changes."""
        user_repo = MagicMock()
        mock_user = User(id=1, username="test", email="test@example.com")
        user_repo.get_by_id.return_value = mock_user
        
        service = UserService(user_repo=user_repo)
        result = service.update_user(1, {})
        
        assert result == mock_user
        user_repo.get_by_id.assert_called_once_with(1)


class TestUrlServiceCoverage:
    """Additional URL service tests."""
    
    def test_get_url_not_found(self):
        """Test getting URL by ID when not found."""
        url_repo = MagicMock()
        url_repo.get_by_id.return_value = None
        
        service = UrlService(url_repo=url_repo)
        result = service.get_url(999)
        
        assert result is None
    
    def test_get_url_by_code_not_found(self):
        """Test getting URL by code when not found."""
        url_repo = MagicMock()
        url_repo.find_by_code.return_value = None
        
        service = UrlService(url_repo=url_repo)
        result = service.get_url_by_code("nonexistent")
        
        assert result is None
    
    def test_update_url_no_changes(self):
        """Test updating URL with no changes."""
        url_repo = MagicMock()
        mock_url = ShortURL(id=1, short_code="abc", original_url="https://example.com")
        url_repo.get_by_id.return_value = mock_url
        
        service = UrlService(url_repo=url_repo)
        result = service.update_url(1, {})
        
        assert result == mock_url
    
    def test_update_url_is_active_string_true(self):
        """Test updating is_active with string 'true'."""
        url_repo = MagicMock()
        mock_url = ShortURL(id=1, short_code="abc", original_url="https://example.com", is_active=True)
        url_repo.update.return_value = mock_url
        
        service = UrlService(url_repo=url_repo)
        result = service.update_url(1, {"is_active": "true"})
        
        url_repo.update.assert_called_once()
    
    def test_update_url_is_active_string_false(self):
        """Test updating is_active with string 'false'."""
        url_repo = MagicMock()
        mock_url = ShortURL(id=1, short_code="abc", original_url="https://example.com", is_active=False)
        url_repo.update.return_value = mock_url
        
        service = UrlService(url_repo=url_repo)
        result = service.update_url(1, {"is_active": "false"})
        
        url_repo.update.assert_called_once()
    
    def test_list_urls_no_filter(self):
        """Test listing all URLs without user filter."""
        url_repo = MagicMock()
        url_repo.get_all.return_value = []
        
        service = UrlService(url_repo=url_repo)
        result = service.list_urls()
        
        url_repo.get_all.assert_called_once()
    
    def test_list_urls_with_user_filter(self):
        """Test listing URLs filtered by user."""
        url_repo = MagicMock()
        url_repo.list_for_user.return_value = []
        
        service = UrlService(url_repo=url_repo)
        result = service.list_urls(user_id=1)
        
        url_repo.list_for_user.assert_called_once_with(user_id=1)


class TestEventServiceCoverage:
    """Additional event service tests."""
    
    def test_list_events_no_filter(self):
        """Test listing all events without filter."""
        event_repo = MagicMock()
        event_repo.get_all.return_value = []
        
        service = EventService(repo=event_repo)
        result = service.list_events()
        
        event_repo.get_all.assert_called_once()
    
    def test_list_events_with_url_filter(self):
        """Test listing events filtered by URL."""
        event_repo = MagicMock()
        event_repo.list_for_url.return_value = []
        
        service = EventService(repo=event_repo)
        result = service.list_events(url_id=1)
        
        event_repo.list_for_url.assert_called_once()
    
    def test_serialize_event_with_user(self):
        """Test serializing event with user."""
        mock_url = MagicMock()
        mock_url.id = 1
        
        mock_user = MagicMock()
        mock_user.id = 2
        
        mock_event = MagicMock()
        mock_event.id = 1
        mock_event.url_id = mock_url
        mock_event.user_id = mock_user
        mock_event.event_type = "created"
        mock_event.timestamp = datetime(2024, 1, 1, 12, 0, 0)
        mock_event.get_details.return_value = {"test": "data"}
        
        result = EventService.serialize_event(mock_event)
        
        assert result["id"] == 1
        assert result["url_id"] == 1
        assert result["user_id"] == 2
        assert result["event_type"] == "created"
    
    def test_serialize_event_without_user(self):
        """Test serializing event without user."""
        mock_url = MagicMock()
        mock_url.id = 1
        
        mock_event = MagicMock()
        mock_event.id = 1
        mock_event.url_id = mock_url
        mock_event.user_id = None
        mock_event.event_type = "accessed"
        mock_event.timestamp = datetime(2024, 1, 1, 12, 0, 0)
        mock_event.get_details.return_value = {}
        
        result = EventService.serialize_event(mock_event)
        
        assert result["user_id"] is None
