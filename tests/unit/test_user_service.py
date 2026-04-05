import pytest
from unittest.mock import MagicMock

from backend.app.services.user_service import UserService
from backend.app.models.user_model import User


@pytest.fixture
def service():
    """Provides UserService initialized with mocked repository dependencies."""
    user_repo = MagicMock()
    service = UserService(user_repo=user_repo)
    return service, user_repo


def test_create_user_success(service):
    svc, user_repo = service
    
    mock_user = User(id=1, username="newuser", email="newuser@example.com")
    user_repo.create.return_value = mock_user
    
    result = svc.create_user(username="newuser", email="newuser@example.com")
    
    assert result == mock_user
    user_repo.create.assert_called_once_with(username="newuser", email="newuser@example.com")


def test_get_user_by_username(service):
    svc, user_repo = service
    
    mock_user = User(id=1, username="testuser")
    user_repo.find_by_username.return_value = mock_user
    
    result = svc.get_user_by_username("testuser")
    
    assert result == mock_user
    user_repo.find_by_username.assert_called_once_with("testuser")


def test_update_user(service):
    svc, user_repo = service
    
    mock_user = User(id=1, username="updateduser")
    user_repo.update.return_value = mock_user
    
    result = svc.update_user(user_id=1, username="updateduser")
    
    assert result == mock_user
    user_repo.update.assert_called_once_with(1, username="updateduser")


def test_get_user_by_id(service):
    svc, user_repo = service
    mock_user = User(id=2, username="lookup")
    user_repo.get_by_id.return_value = mock_user

    assert svc.get_user(2) == mock_user


def test_list_users_applies_offset(service):
    svc, user_repo = service
    user_repo.get_all.return_value = []

    svc.list_users(page=3, per_page=25)

    user_repo.get_all.assert_called_once()
    _, kwargs = user_repo.get_all.call_args
    assert kwargs["skip"] == 50
    assert kwargs["limit"] == 25


def test_delete_user_delegates_to_repo(service):
    svc, user_repo = service

    svc.delete_user(4)

    user_repo.delete.assert_called_once_with(4)


def test_bulk_import_csv_imports_valid_rows_and_ignores_invalid(service):
    svc, user_repo = service
    csv_content = """id,username,email,created_at
1,alice,alice@example.com,2026-04-05 12:00:00
bad,bob,bob@example.com,2026-04-05 12:00:00
2,charlie,charlie@example.com,invalid-date
"""

    imported = svc.bulk_import_csv(csv_content)

    assert imported == 2
    assert user_repo.get_or_create_for_import.call_count == 2


def test_bulk_import_resets_sequence_when_rows_imported(service):
    svc, user_repo = service
    csv_content = "id,username,email,created_at\n1,alice,alice@example.com,2026-04-05 12:00:00\n"

    with pytest.MonkeyPatch.context() as mp:
        execute_sql = MagicMock()
        mp.setattr("backend.app.config.database.db", type("DB", (), {"execute_sql": execute_sql})())
        imported = svc.bulk_import_csv(csv_content)

    assert imported == 1
    execute_sql.assert_called_once()
