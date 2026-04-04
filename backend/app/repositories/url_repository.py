from typing import List

from backend.app.models import ShortURL
from backend.app.repositories.base_repository import BaseRepository


class UrlRepository(BaseRepository[ShortURL]):
    def __init__(self):
        super().__init__(ShortURL)

    def find_by_code(self, short_code: str) -> ShortURL | None:
        return self.get_one(short_code=short_code)

    def list_for_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[ShortURL]:
        return self.get_all(skip=skip, limit=limit, order_by=ShortURL.id, user_id=user_id)
        