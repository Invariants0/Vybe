import json
from datetime import datetime, timezone

from peewee import BigAutoField, CharField, DateTimeField, ForeignKeyField, TextField

from backend.app.config.database import BaseModel
from backend.app.models.url_model import ShortURL
from backend.app.models.user_model import User


def utcnow():
    return datetime.now(timezone.utc)


class Event(BaseModel):
    """
    Analytics event.  event_type is 'created' or 'accessed'.
    details is a JSON blob: {"short_code": "...", "original_url": "..."}
    Table: events
    """

    id = BigAutoField()
    url_id = ForeignKeyField(
        ShortURL,
        backref="events",
        column_name="url_id",
        index=True,
        on_delete="CASCADE",
    )
    user_id = ForeignKeyField(
        User,
        backref="events",
        column_name="user_id",
        null=True,
        index=True,
        on_delete="SET NULL",
    )
    event_type = CharField(max_length=32, index=True)  # "created" | "accessed"
    timestamp = DateTimeField(default=utcnow, index=True)
    details = TextField(null=True)  # stored as JSON string

    class Meta:
        table_name = "events"

    def get_details(self):
        """Return details as a dict (or empty dict if missing/invalid)."""
        if not self.details:
            return {}
        try:
            return json.loads(self.details)
        except (TypeError, ValueError):
            return {}

    @classmethod
    def create_for_url(cls, short_url, event_type: str, user=None):
        details = json.dumps(
            {
                "short_code": short_url.short_code,
                "original_url": short_url.original_url,
            }
        )
        return cls.create(
            url_id=short_url,
            user_id=user or short_url.user_id,
            event_type=event_type,
            timestamp=utcnow(),
            details=details,
        )
