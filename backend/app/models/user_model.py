from datetime import datetime, timezone

from peewee import BigAutoField, CharField, DateTimeField

from backend.app.config import BaseModel


def utcnow():
    return datetime.now(timezone.utc)


class User(BaseModel):
    id = BigAutoField()
    username = CharField(unique=True, max_length=128, index=True)
    email = CharField(unique=True, max_length=254, index=True)
    created_at = DateTimeField(default=utcnow, index=True)

    class Meta:
        table_name = "users"
