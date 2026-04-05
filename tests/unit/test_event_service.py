from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from backend.app.services.event_service import EventService


def test_create_event_requires_url_id():
    service = EventService(repo=MagicMock())

    with pytest.raises(ValueError, match="url_id is required"):
        service.create_event(url_id=None, event_type="created")


def test_create_event_requires_event_type():
    service = EventService(repo=MagicMock())

    with pytest.raises(ValueError, match="event_type is required"):
        service.create_event(url_id=1, event_type="")


def test_create_event_requires_existing_short_url():
    service = EventService(repo=MagicMock())

    with patch(
        "backend.app.services.event_service.ShortURL.get_or_none", return_value=None
    ):
        with pytest.raises(ValueError, match="URL with id 1 does not exist"):
            service.create_event(url_id=1, event_type="created")


def test_create_event_serializes_details_and_saves():
    repo = MagicMock()
    created_event = MagicMock()
    repo.create.return_value = created_event
    service = EventService(repo=repo)
    short_url = MagicMock()
    short_url.short_code = "abc123"
    short_url.original_url = "https://example.com"

    with patch(
        "backend.app.services.event_service.ShortURL.get_or_none",
        return_value=short_url,
    ):
        result = service.create_event(
            url_id=1, event_type="created", user_id=7, details={"source": "manual"}
        )

    assert result is created_event
    repo.create.assert_called_once()
    _, kwargs = repo.create.call_args
    assert kwargs["url_id"] == 1
    assert kwargs["user_id"] == 7
    assert json.loads(kwargs["details"]) == {"source": "manual"}
