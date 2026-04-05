from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from backend.app.config import database


def test_get_pool_snapshot_without_initialized_db():
    with patch.object(database.db, "obj", None, create=True):
        assert database.get_pool_snapshot() == {"open": 0, "in_use": 0, "max": 0}


def test_get_pool_snapshot_reads_pool_state():
    fake_pool = SimpleNamespace(
        _connections={1, 2, 3},
        _in_use={1: object()},
        _max_connections=8,
    )

    with patch.object(database, "db", SimpleNamespace(obj=fake_pool)):
        assert database.get_pool_snapshot() == {"open": 3, "in_use": 1, "max": 8}


def test_record_pool_metrics_updates_prometheus_gauges():
    with patch("backend.app.config.database.DB_POOL_CONNECTIONS_OPEN.set") as set_open, patch(
        "backend.app.config.database.DB_POOL_CONNECTIONS_IN_USE.set"
    ) as set_in_use, patch("backend.app.config.database.DB_POOL_MAX_CONNECTIONS.set") as set_max, patch(
        "backend.app.config.database.get_pool_snapshot",
        return_value={"open": 4, "in_use": 2, "max": 12},
    ):
        snapshot = database.record_pool_metrics()

    assert snapshot == {"open": 4, "in_use": 2, "max": 12}
    set_open.assert_called_once_with(4)
    set_in_use.assert_called_once_with(2)
    set_max.assert_called_once_with(12)


def test_ping_db_connects_when_closed():
    fake_db = MagicMock()
    fake_db.is_closed.return_value = True

    with patch.object(database, "db", fake_db), patch("backend.app.config.database.record_pool_metrics"):
        database.ping_db()

    fake_db.connect.assert_called_once_with(reuse_if_open=True)
    fake_db.execute_sql.assert_called_once_with("SELECT 1")
