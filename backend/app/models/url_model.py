from datetime import datetime, timezone

from peewee import (
    BigAutoField,
    BooleanField,
    CharField,
    DateTimeField,
    ForeignKeyField,
    IntegerField,
    TextField,
)

from backend.app.config.database import BaseModel
from backend.app.models.user_model import User


def utcnow():
    return datetime.now(timezone.utc)


class ShortURL(BaseModel):
    """
    Primary URL model aligned to the evaluator API contract and seed data.
    Table: urls
    """

    id = BigAutoField()
    user_id = ForeignKeyField(User, backref="urls", column_name="user_id", null=True, index=True)
    short_code = CharField(unique=True, max_length=32, index=True)
    original_url = TextField()
    title = CharField(null=True, max_length=512)
    is_active = BooleanField(default=True, index=True)
    created_at = DateTimeField(default=utcnow, index=True)
    updated_at = DateTimeField(default=utcnow)

    class Meta:
        table_name = "urls"

    def save(self, *args, **kwargs):
        self.updated_at = utcnow()
        return super().save(*args, **kwargs)


class LinkVisit(BaseModel):
    """
    Per-redirect visit tracking. Kept for backwards compat with /api/v1/links.
    Table: link_visits
    """

    id = BigAutoField()
    short_url = ForeignKeyField(ShortURL, backref="visits", on_delete="CASCADE")
    ip_address = CharField(null=True, max_length=64)
    user_agent = TextField(null=True)
    referer = TextField(null=True)
    accessed_at = DateTimeField(default=utcnow, index=True)

    class Meta:
        table_name = "link_visits"
