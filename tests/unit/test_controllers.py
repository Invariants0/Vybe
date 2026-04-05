from __future__ import annotations

import io
import json
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError
from werkzeug.datastructures import FileStorage, MultiDict
from werkzeug.exceptions import BadRequest

from backend.app.controllers.event_controller import EventController
from backend.app.controllers.url_controller import UrlController
from backend.app.controllers.user_controller import UserController
from backend.app.validators.schemas import CreateUserSchema


def _request(
    payload=None,
    *,
    args=None,
    headers=None,
    files=None,
    bad_json=False,
    content_type="application/json",
):
    req = MagicMock()
    req.args = MultiDict(args or {})
    req.headers = headers or {}
    req.files = files or {}
    req.content_type = content_type
    if bad_json:
        req.get_json.side_effect = BadRequest("malformed json")
    else:
        req.get_json.return_value = payload
    return req


def _dt():
    return datetime(2026, 4, 5, 12, 0, tzinfo=timezone.utc)


def _user(user_id=1, username="alice", email="alice@example.com"):
    return SimpleNamespace(id=user_id, username=username, email=email, created_at=_dt())


def _url(url_id=1, user_id=1, code="abc123", active=True):
    return SimpleNamespace(
        id=url_id,
        user_id=SimpleNamespace(id=user_id),
        short_code=code,
        original_url="https://example.com",
        title="Example",
        is_active=active,
        created_at=_dt(),
        updated_at=_dt(),
    )


def _event(event_id=1, url_id=1, user_id=1, event_type="created"):
    return SimpleNamespace(
        id=event_id,
        url_id=SimpleNamespace(id=url_id),
        user_id=SimpleNamespace(id=user_id) if user_id is not None else None,
        event_type=event_type,
        timestamp=_dt(),
        get_details=lambda: {"source": "test"},
    )


class TestUrlController:
    def test_create_url_success_and_idempotency_cache(self, app):
        controller = UrlController(MagicMock())
        controller.set_config({"REDIS_ENABLED": True})
        created = _url()
        controller.url_service.create_url.return_value = created

        request = _request(
            {"user_id": 1, "original_url": "https://example.com", "title": "Example"},
            headers={"Idempotency-Key": "idem-1"},
        )

        with (
            app.app_context(),
            patch(
                "backend.app.controllers.url_controller.cache_get", return_value=None
            ),
            patch("backend.app.controllers.url_controller.cache_set") as cache_set,
        ):
            response, status = controller.create_url(request)

        assert status == 201
        assert response.get_json()["short_code"] == "abc123"
        controller.url_service.create_url.assert_called_once()
        cache_set.assert_called_once()

    def test_create_url_returns_cached_idempotent_response(self, app):
        controller = UrlController(MagicMock())
        request = _request(headers={"Idempotency-Key": "idem-2"})
        cached = json.dumps({"id": 9, "short_code": "cached"})

        with (
            app.app_context(),
            patch(
                "backend.app.controllers.url_controller.cache_get", return_value=cached
            ),
        ):
            response, status = controller.create_url(request)

        assert status == 201
        assert response.get_json()["short_code"] == "cached"
        controller.url_service.create_url.assert_not_called()

    def test_create_url_rejects_empty_payload(self, app):
        controller = UrlController(MagicMock())

        with app.app_context():
            response, status = controller.create_url(_request(None))

        assert status == 400
        assert response.get_json()["error"] == "bad_request"

    def test_list_urls_uses_cache(self, app):
        controller = UrlController(MagicMock())
        request = _request(args={"user_id": "1", "is_active": "true"})
        cached = json.dumps([{"id": 1}])

        with (
            app.app_context(),
            patch(
                "backend.app.controllers.url_controller.cache_get", return_value=cached
            ),
        ):
            response, status = controller.list_urls(request)

        assert status == 200
        assert response.get_json() == [{"id": 1}]
        controller.url_service.list_urls.assert_not_called()

    def test_list_urls_fetches_and_caches(self, app):
        controller = UrlController(MagicMock())
        controller.url_service.list_urls.return_value = [_url()]

        with (
            app.app_context(),
            patch(
                "backend.app.controllers.url_controller.cache_get", return_value=None
            ),
            patch("backend.app.controllers.url_controller.cache_set") as cache_set,
        ):
            response, status = controller.list_urls(_request(args={"user_id": "1"}))

        assert status == 200
        assert response.get_json()[0]["id"] == 1
        controller.url_service.list_urls.assert_called_once_with(
            user_id=1, is_active=None, page=1, per_page=50
        )
        cache_set.assert_called_once()

    def test_get_url_returns_not_found(self, app):
        controller = UrlController(MagicMock())
        controller.url_service.get_url.return_value = None

        with (
            app.app_context(),
            patch(
                "backend.app.controllers.url_controller.cache_get", return_value=None
            ),
        ):
            response, status = controller.get_url(999)

        assert status == 404
        assert response.get_json()["error"] == "not_found"

    def test_get_url_reads_from_cache(self, app):
        controller = UrlController(MagicMock())
        cached = json.dumps({"id": 4, "short_code": "from-cache"})

        with (
            app.app_context(),
            patch(
                "backend.app.controllers.url_controller.cache_get", return_value=cached
            ),
        ):
            response, status = controller.get_url(4)

        assert status == 200
        assert response.get_json()["short_code"] == "from-cache"

    def test_update_url_success(self, app):
        controller = UrlController(MagicMock())
        controller.url_service.update_url.return_value = _url(active=False)

        with (
            app.app_context(),
            patch(
                "backend.app.controllers.url_controller.cache_delete"
            ) as cache_delete,
        ):
            response, status = controller.update_url(1, _request({"is_active": False}))

        assert status == 200
        assert response.get_json()["is_active"] is False
        cache_delete.assert_called_once_with("url:1", None)

    def test_update_url_validation_error(self, app):
        controller = UrlController(MagicMock())

        with app.app_context():
            response, status = controller.update_url(
                1, _request({"is_active": "definitely"})
            )

        assert status == 422
        assert response.get_json()["error"] == "validation_error"

    def test_delete_url_is_idempotent(self, app):
        controller = UrlController(MagicMock())
        controller.url_service.get_url.return_value = None

        with app.app_context():
            response, status = controller.delete_url(7)

        assert status == 204
        assert response.get_json() == {}
        controller.url_service.delete_url.assert_not_called()


class TestUserController:
    def test_create_user_success(self, app):
        controller = UserController(MagicMock())
        controller.user_service.create_user.return_value = _user()

        with app.app_context():
            response, status = controller.create_user(
                _request({"username": "alice", "email": "alice@example.com"})
            )

        assert status == 201
        assert response.get_json()["username"] == "alice"

    def test_create_user_handles_bad_json(self, app):
        controller = UserController(MagicMock())

        with app.app_context():
            response, status = controller.create_user(_request(bad_json=True))

        assert status == 400
        assert response.get_json()["error"] == "bad_request"

    def test_create_user_validation_error(self, app):
        controller = UserController(MagicMock())

        with app.app_context():
            response, status = controller.create_user(
                _request({"username": "alice", "email": "bad"})
            )

        assert status == 422
        assert response.get_json()["error"] == "validation_error"

    def test_create_user_json_required(self, app):
        controller = UserController(MagicMock())

        with app.app_context():
            response, status = controller.create_user(_request(payload=None))

        assert status == 400
        assert response.get_json()["error"] == "bad_request"

    def test_create_user_rejects_non_dict_payload(self, app):
        controller = UserController(MagicMock())

        with app.app_context():
            response, status = controller.create_user(
                _request(payload=["not", "a", "dict"])
            )

        assert status == 400
        assert response.get_json()["error"] == "bad_request"
        assert response.get_json()["message"] == "Payload must be a JSON object"

    def test_list_users_uses_get_all_users_when_unpaged(self, app):
        controller = UserController(MagicMock())
        controller.user_service.get_all_users.return_value = [_user()]

        with (
            app.app_context(),
            patch(
                "backend.app.controllers.user_controller.cache_get", return_value=None
            ),
            patch("backend.app.controllers.user_controller.cache_set"),
        ):
            response, status = controller.list_users(_request(args={}))

        assert status == 200
        assert response.get_json()[0]["id"] == 1
        controller.user_service.get_all_users.assert_called_once()

    def test_list_users_uses_pagination_when_requested(self, app):
        controller = UserController(MagicMock())
        controller.user_service.list_users.return_value = [_user(user_id=2)]

        with (
            app.app_context(),
            patch(
                "backend.app.controllers.user_controller.cache_get", return_value=None
            ),
            patch("backend.app.controllers.user_controller.cache_set"),
        ):
            response, status = controller.list_users(
                _request(args={"page": "2", "per_page": "10"})
            )

        assert status == 200
        assert response.get_json()[0]["id"] == 2
        controller.user_service.list_users.assert_called_once_with(page=2, per_page=10)

    def test_get_user_not_found(self, app):
        controller = UserController(MagicMock())
        controller.user_service.get_user.return_value = None

        with (
            app.app_context(),
            patch(
                "backend.app.controllers.user_controller.cache_get", return_value=None
            ),
        ):
            response, status = controller.get_user(999)

        assert status == 404
        assert response.get_json()["error"] == "not_found"

    def test_update_user_success(self, app):
        controller = UserController(MagicMock())
        controller.user_service.update_user.return_value = _user(username="updated")

        with (
            app.app_context(),
            patch(
                "backend.app.controllers.user_controller.cache_delete"
            ) as cache_delete,
        ):
            response, status = controller.update_user(
                1, _request({"username": "updated"})
            )

        assert status == 200
        assert response.get_json()["username"] == "updated"
        cache_delete.assert_called_once_with("user:1", None)

    def test_delete_user_is_idempotent(self, app):
        controller = UserController(MagicMock())
        controller.user_service.get_user.return_value = None

        with app.app_context():
            response, status = controller.delete_user(3)

        assert status == 204
        assert response.get_json() == {}

    def test_bulk_import_success(self, app):
        controller = UserController(MagicMock())
        controller.user_service.bulk_import_csv.return_value = 2
        csv_file = FileStorage(
            stream=io.BytesIO(b"id,username,email\n1,a,a@example.com\n"),
            filename="users.csv",
        )

        with app.app_context():
            response, status = controller.bulk_import(
                _request(files={"file": csv_file})
            )

        assert status == 201
        assert response.get_json()["count"] == 2

    def test_bulk_import_requires_file(self, app):
        controller = UserController(MagicMock())

        with app.app_context():
            response, status = controller.bulk_import(_request(files={}))

        assert status == 400
        assert response.get_json()["error"] == "bad_request"


class TestEventController:
    def test_list_events_uses_cache(self, app):
        controller = EventController(MagicMock())
        cached = json.dumps([{"id": 1, "event_type": "created"}])

        with (
            app.app_context(),
            patch(
                "backend.app.controllers.event_controller.cache_get",
                return_value=cached,
            ),
        ):
            response, status = controller.list_events(_request(args={"url_id": "1"}))

        assert status == 200
        assert response.get_json()[0]["event_type"] == "created"

    def test_list_events_filters_and_serializes(self, app):
        controller = EventController(MagicMock())
        controller.event_service.list_events.return_value = [_event()]
        controller.event_service.serialize_event.side_effect = lambda event: {
            "id": event.id,
            "event_type": event.event_type,
        }

        with (
            app.app_context(),
            patch(
                "backend.app.controllers.event_controller.cache_get", return_value=None
            ),
            patch("backend.app.controllers.event_controller.cache_set"),
        ):
            response, status = controller.list_events(
                _request(
                    args={
                        "url_id": "1",
                        "user_id": "2",
                        "event_type": "created",
                        "page": "2",
                        "per_page": "10",
                    }
                )
            )

        assert status == 200
        assert response.get_json() == [{"id": 1, "event_type": "created"}]
        controller.event_service.list_events.assert_called_once_with(
            url_id=1,
            user_id=2,
            event_type="created",
            page=2,
            per_page=10,
        )

    def test_create_event_success(self, app):
        controller = EventController(MagicMock())
        event = _event(event_type="accessed")
        controller.event_service.create_event.return_value = event
        controller.event_service.serialize_event.return_value = {
            "id": 1,
            "event_type": "accessed",
        }

        with app.app_context():
            response, status = controller.create_event(
                _request(
                    {
                        "url_id": 1,
                        "user_id": 2,
                        "event_type": "accessed",
                        "details": {"source": "test"},
                    }
                )
            )

        assert status == 201
        assert response.get_json()["event_type"] == "accessed"

    def test_create_event_requires_payload(self, app):
        controller = EventController(MagicMock())

        with app.app_context():
            response, status = controller.create_event(_request(None))

        assert status == 400
        assert response.get_json()["error"] == "bad_request"

    def test_create_event_rejects_string_payload(self, app):
        controller = EventController(MagicMock())

        with app.app_context():
            response, status = controller.create_event(
                _request("just a string, not a chest")
            )

        assert status == 400
        assert response.get_json()["error"] == "bad_request"
        controller.event_service.create_event.assert_not_called()


def test_base_controller_handles_pydantic_error(app):
    controller = UserController(MagicMock())

    with app.app_context():
        with pytest.raises(ValidationError) as exc:
            CreateUserSchema(username="alice", email="not-an-email")
        response, status = controller.handle_error(exc.value, "create_user")

    assert status == 422
    assert response.get_json()["error"] == "validation_error"


def test_base_controller_expose_error_details(app):
    controller = UserController(MagicMock())
    app.config["EXPOSE_ERROR_DETAILS"] = True

    with app.app_context():
        response, status = controller.handle_error(RuntimeError("boom"), "create_user")

    body = response.get_json()
    assert status == 500
    assert body["error_type"] == "RuntimeError"
    assert body["error_detail"] == "boom"
    assert body["operation"] == "create_user"


def test_base_controller_handles_conflict_error(app):
    from backend.app.config.errors import ConflictError

    controller = UserController(MagicMock())

    with app.app_context():
        response, status = controller.handle_error(
            ConflictError("duplicate"), "create_user"
        )

    assert status == 409
    assert response.get_json()["error"] == "conflict"


def test_base_controller_handles_forbidden_error(app):
    from backend.app.config.errors import ForbiddenError

    controller = UserController(MagicMock())

    with app.app_context():
        response, status = controller.handle_error(
            ForbiddenError("nope"), "update_user"
        )

    assert status == 403
    assert response.get_json()["error"] == "forbidden"


def test_base_controller_handles_gone_error(app):
    from backend.app.config.errors import GoneError

    controller = UserController(MagicMock())

    with app.app_context():
        response, status = controller.handle_error(GoneError("deleted"), "get_user")

    assert status == 410
    assert response.get_json()["error"] == "gone"


def test_base_controller_reports_to_sentry(app):
    controller = UserController(MagicMock())
    app.config["SENTRY_DSN"] = "https://example@sentry.invalid/1"

    with (
        app.app_context(),
        patch(
            "backend.app.controllers.base_controller.sentry_sdk.capture_exception"
        ) as capture_exception,
    ):
        response, status = controller.handle_error(RuntimeError("boom"), "create_user")

    assert status == 500
    capture_exception.assert_called_once()
