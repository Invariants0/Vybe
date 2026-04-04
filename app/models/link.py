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

from app.database import BaseModel


def utcnow():
    return datetime.now(timezone.utc)


class ShortURL(BaseModel):
    id = BigAutoField()
    code = CharField(unique=True, max_length=32, index=True)
    original_url = TextField()
    is_active = BooleanField(default=True, index=True)
    click_count = IntegerField(default=0)
    creator_ip = CharField(null=True, max_length=64)
    created_at = DateTimeField(default=utcnow, index=True)
    updated_at = DateTimeField(default=utcnow)
    expires_at = DateTimeField(null=True, index=True)
    last_accessed_at = DateTimeField(null=True)

    class Meta:
        table_name = "short_urls"

    def save(self, *args, **kwargs):
        self.updated_at = utcnow()
        return super().save(*args, **kwargs)


class LinkVisit(BaseModel):
    id = BigAutoField()
    short_url = ForeignKeyField(ShortURL, backref="visits", on_delete="CASCADE")
    ip_address = CharField(null=True, max_length=64)
    user_agent = TextField(null=True)
    referer = TextField(null=True)
    accessed_at = DateTimeField(default=utcnow, index=True)

    class Meta:
        table_name = "link_visits"
