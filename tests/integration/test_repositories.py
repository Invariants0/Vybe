from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import patch

from backend.app.config.database import db
from backend.app.models import Event, ShortURL, User
from backend.app.repositories.base_repository import BaseRepository
from backend.app.repositories.event_repository import EventRepository
from backend.app.repositories.url_repository import UrlRepository
from backend.app.repositories.user_repository import UserRepository


def _seed_urls():
    user = User.create(username="repo-user", email="repo@example.com")
    urls = [
        ShortURL.create(
            user_id=user,
            short_code=f"code-{index}",
            original_url=f"https://example.com/{index}",
            title=f"Title {index}",
            is_active=index % 2 == 0,
        )
        for index in range(5)
    ]
    for index, url in enumerate(urls):
        Event.create(
            url_id=url,
            user_id=user,
            event_type="created" if index % 2 == 0 else "accessed",
            details='{"source":"repo-test"}',
        )
    return user, urls


def test_base_repository_crud_cycle(app):
    with app.app_context():
        repo = BaseRepository(User)

        created = repo.create(username="crud-user", email="crud@example.com")
        fetched = repo.get_by_id(created.id)
        updated = repo.update(created.id, username="crud-user-2")
        exists_before_delete = repo.exists(username="crud-user-2")
        deleted = repo.delete(created.id)
        exists_after_delete = repo.exists(username="crud-user-2")

    assert fetched.id == created.id
    assert updated.username == "crud-user-2"
    assert exists_before_delete is True
    assert deleted is True
    assert exists_after_delete is False


def test_url_repository_filters_and_paginates(app):
    with app.app_context():
        user, urls = _seed_urls()
        repo = UrlRepository()

        first_page = repo.list_for_user(user.id, skip=0, limit=2)
        second_page = repo.list_for_user(user.id, skip=2, limit=2)
        active_urls = repo.get_all(skip=0, limit=10, order_by=ShortURL.id, is_active=True)
        by_code = repo.find_by_code(urls[0].short_code)

    assert [url.short_code for url in first_page] == ["code-0", "code-1"]
    assert [url.short_code for url in second_page] == ["code-2", "code-3"]
    assert all(url.is_active for url in active_urls)
    assert by_code.id == urls[0].id


def test_url_repository_avoids_n_plus_one_on_user_access(app):
    with app.app_context():
        user, _ = _seed_urls()
        repo = UrlRepository()

        with patch.object(db.obj, "execute_sql", wraps=db.obj.execute_sql) as execute_sql:
            urls = repo.list_for_user(user.id, skip=0, limit=5)
            user_ids = [url.user_id.id for url in urls]

    assert user_ids == [user.id] * 5
    assert execute_sql.call_count == 1


def test_user_repository_import_preserves_existing_users(app):
    created_at = datetime(2026, 4, 5, tzinfo=timezone.utc)

    with app.app_context():
        repo = UserRepository()
        first = repo.get_or_create_for_import(10, "imported", "imported@example.com", created_at)
        second = repo.get_or_create_for_import(10, "imported-duplicate", "duplicate@example.com", created_at)

    assert first.id == second.id
    assert second.username == "imported"


def test_event_repository_filtering_pagination_and_logging(app):
    with app.app_context():
        user, urls = _seed_urls()
        repo = EventRepository()

        filtered = repo.list_filtered(url_id=urls[0].id, event_type="created", skip=0, limit=10)
        paginated = repo.list_for_url(urls[0].id, skip=0, limit=1)
        logged = repo.log_event(urls[0], "accessed", user=user)

    assert [event.url_id.id for event in filtered] == [urls[0].id]
    assert len(paginated) == 1
    assert logged.event_type == "accessed"
    assert logged.get_details()["short_code"] == urls[0].short_code


def test_event_repository_avoids_n_plus_one_on_related_access(app):
    with app.app_context():
        user, _ = _seed_urls()
        repo = EventRepository()

        with patch.object(db.obj, "execute_sql", wraps=db.obj.execute_sql) as execute_sql:
            events = repo.list_filtered(user_id=user.id, skip=0, limit=5)
            payload = [(event.url_id.short_code, event.user_id.id) for event in events]

    assert len(payload) == 5
    assert execute_sql.call_count == 1
