from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock

from backend.app.services.event_service import EventService
from backend.app.services.url_service import UrlService
from backend.app.services.user_service import UserService


class TestUserServiceCoverage:
    def test_get_user_by_username_not_found(self):
        user_repo = MagicMock()
        user_repo.find_by_username.return_value = None

        service = UserService(user_repo=user_repo)

        assert service.get_user_by_username("missing") is None

    def test_update_user_with_kwargs(self):
        user_repo = MagicMock()
        updated = MagicMock()
        user_repo.update.return_value = updated

        service = UserService(user_repo=user_repo)

        assert service.update_user(1, username="updated") is updated
        user_repo.update.assert_called_once_with(1, username="updated")

    def test_update_user_no_changes_returns_existing_user(self):
        user_repo = MagicMock()
        existing = MagicMock()
        user_repo.get_by_id.return_value = existing

        service = UserService(user_repo=user_repo)

        assert service.update_user(1, {}) is existing
        user_repo.get_by_id.assert_called_once_with(1)


class TestUrlServiceCoverage:
    def test_get_url_not_found(self):
        url_repo = MagicMock()
        url_repo.get_by_id.return_value = None

        service = UrlService(url_repo=url_repo)

        assert service.get_url(999) is None

    def test_get_url_by_code_not_found(self):
        url_repo = MagicMock()
        url_repo.find_by_code.return_value = None

        service = UrlService(url_repo=url_repo)

        assert service.get_url_by_code("missing") is None

    def test_update_url_no_changes_returns_existing_url(self):
        url_repo = MagicMock()
        existing = MagicMock()
        url_repo.get_by_id.return_value = existing

        service = UrlService(url_repo=url_repo)

        assert service.update_url(1, {}) is existing
        url_repo.get_by_id.assert_called_once_with(1)

    def test_update_url_normalizes_boolean_strings(self):
        url_repo = MagicMock()
        updated = MagicMock()
        updated.short_code = "abc123"
        url_repo.update.return_value = updated

        service = UrlService(url_repo=url_repo)

        service.update_url(1, {"is_active": "false"})

        url_repo.update.assert_called_once_with(1, is_active=False)

    def test_list_urls_applies_filters(self):
        url_repo = MagicMock()
        url_repo.get_all.return_value = []

        service = UrlService(url_repo=url_repo)

        service.list_urls(user_id=10, is_active=True)

        url_repo.get_all.assert_called_once()
        _, kwargs = url_repo.get_all.call_args
        assert kwargs["user_id"] == 10
        assert kwargs["is_active"] is True


class TestEventServiceCoverage:
    def test_list_events_uses_filtered_repository_query(self):
        event_repo = MagicMock()
        event_repo.list_filtered.return_value = []

        service = EventService(repo=event_repo)

        service.list_events(
            url_id=1, user_id=2, event_type="created", page=2, per_page=25
        )

        event_repo.list_filtered.assert_called_once_with(
            url_id=1,
            user_id=2,
            event_type="created",
            skip=25,
            limit=25,
        )

    def test_serialize_event_with_user(self):
        mock_url = MagicMock()
        mock_url.id = 1
        mock_user = MagicMock()
        mock_user.id = 2
        mock_event = MagicMock()
        mock_event.id = 3
        mock_event.url_id = mock_url
        mock_event.user_id = mock_user
        mock_event.event_type = "created"
        mock_event.timestamp = datetime(2024, 1, 1, 12, 0, 0)
        mock_event.get_details.return_value = {"ok": True}

        payload = EventService.serialize_event(mock_event)

        assert payload["id"] == 3
        assert payload["short_url_id"] == 1
        assert payload["user_id"] == 2
        assert payload["details"] == {"ok": True}

    def test_serialize_event_without_user(self):
        mock_url = MagicMock()
        mock_url.id = 1
        mock_event = MagicMock()
        mock_event.id = 4
        mock_event.url_id = mock_url
        mock_event.user_id = None
        mock_event.event_type = "accessed"
        mock_event.timestamp = datetime(2024, 1, 1, 12, 0, 0)
        mock_event.get_details.return_value = {}

        payload = EventService.serialize_event(mock_event)

        assert payload["user_id"] is None
