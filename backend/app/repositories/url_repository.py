from typing import List

from peewee import JOIN

from backend.app.models import ShortURL, User
from backend.app.repositories.base_repository import BaseRepository


class UrlRepository(BaseRepository[ShortURL]):
    def __init__(self):
        super().__init__(ShortURL)

    def get_by_id(self, entity_id: int) -> ShortURL | None:
        return (
            ShortURL.select(ShortURL, User)
            .join(User, JOIN.LEFT_OUTER, on=(ShortURL.user_id == User.id))
            .where(ShortURL.id == entity_id)
            .first()
        )

    def find_by_code(self, short_code: str) -> ShortURL | None:
        return (
            ShortURL.select(ShortURL, User)
            .join(User, JOIN.LEFT_OUTER, on=(ShortURL.user_id == User.id))
            .where(ShortURL.short_code == short_code)
            .first()
        )

    def get_all(self, skip: int = 0, limit: int = 100, order_by=None, **filters) -> List[ShortURL]:
        query = (
            ShortURL.select(ShortURL, User)
            .join(User, JOIN.LEFT_OUTER, on=(ShortURL.user_id == User.id))
        )
        if order_by is not None:
            query = query.order_by(order_by)
        for key, value in filters.items():
            query = query.where(getattr(ShortURL, key) == value)
        return list(query.offset(skip).limit(limit))

    def list_for_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[ShortURL]:
        return self.get_all(skip=skip, limit=limit, order_by=ShortURL.id, user_id=user_id)
        
