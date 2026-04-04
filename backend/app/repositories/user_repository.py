from datetime import datetime

from backend.app.models import User
from backend.app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)

    def find_by_email(self, email: str) -> User | None:
        return self.get_one(email=email)

    def find_by_username(self, username: str) -> User | None:
        return self.get_one(username=username)

    def get_or_create_for_import(self, user_id: int, username: str, email: str, created_at: datetime) -> User:
        user, _ = User.get_or_create(
            id=user_id,
            defaults={
                "username": username,
                "email": email,
                "created_at": created_at
            }
        )
        return user
