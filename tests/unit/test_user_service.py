import pytest
from unittest.mock import MagicMock
from backend.app.services.user_service import UserService
from backend.app.models.user_model import User


@pytest.fixture
def service():
    # Mock repositories
    user_repo = MagicMock()
    
    # Initialize service with mocked dependencies
    service = UserService(
        user_repo=user_repo
    )
    return service, user_repo


def test_create_user_success(service):
    """Bronze Tier: Successfully create a user via service layer."""
    svc, user_repo = service
    
    mock_user = User(id=1, username="newuser", email="newuser@example.com")
    user_repo.create.return_value = mock_user
    
    result = svc.create_user(username="newuser", email="newuser@example.com")
    
    assert result == mock_user
    user_repo.create.assert_called_once_with(username="newuser", email="newuser@example.com")


def test_get_user_by_username(service):
    """Bronze Tier: Fetch user by username."""
    svc, user_repo = service
    
    mock_user = User(id=1, username="testuser")
    user_repo.find_by_username.return_value = mock_user
    
    result = svc.get_user_by_username("testuser")
    
    assert result == mock_user
    user_repo.find_by_username.assert_called_once_with("testuser")


def test_update_user(service):
    """Bronze Tier: Update user details."""
    svc, user_repo = service
    
    mock_user = User(id=1, username="updateduser")
    user_repo.update.return_value = mock_user
    
    result = svc.update_user(user_id=1, username="updateduser")
    
    assert result == mock_user
    user_repo.update.assert_called_once_with(1, username="updateduser")
