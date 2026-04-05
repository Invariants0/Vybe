import csv
import io
from datetime import datetime
from typing import Any, Dict, List, Optional

from peewee import IntegrityError

from backend.app.models import User
from backend.app.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, config: Optional[Dict[str, Any]] = None, user_repo: Optional[UserRepository] = None):
        self.config = config or {}
        self.repo = user_repo or UserRepository()

    def create_user(self, username: str, email: str) -> User:
        return self.repo.create(username=username, email=email)

    def get_user(self, user_id: int) -> Optional[User]:
        return self.repo.get_by_id(user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        return self.repo.find_by_username(username)

    def get_all_users(self) -> List[User]:
        return list(User.select())

    def list_users(self, page: int = 1, per_page: int = 50) -> List[User]:
        skip = (page - 1) * per_page
        return self.repo.get_all(skip=skip, limit=per_page, order_by=User.id)

    def update_user(self, user_id: int, data: Dict[str, Any] = None, **kwargs) -> Optional[User]:
        if data is None:
            data = kwargs
        else:
            data = {**data, **kwargs}
            
        updates = {}
        if "username" in data:
            updates["username"] = data["username"]
        if "email" in data:
            updates["email"] = data["email"]

        if not updates:
            return self.get_user(user_id)

        return self.repo.update(user_id, **updates)

    def delete_user(self, user_id: int) -> None:
        self.repo.delete(user_id)

    def bulk_import_csv(self, file_content: str) -> int:
        f = io.StringIO(file_content.strip())
        reader = csv.DictReader(f)
        imported_count = 0

        for row in reader:
            try:
                raw_created_at = row.get("created_at", "").strip()
                if raw_created_at.endswith("x"):
                    raw_created_at = raw_created_at[:-1]
                
                try:
                    created_at = datetime.strptime(raw_created_at, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    created_at = datetime.now()

                self.repo.get_or_create_for_import(
                    user_id=int(row["id"]),
                    username=row["username"],
                    email=row["email"],
                    created_at=created_at
                )
                imported_count += 1
            except (KeyError, ValueError, IntegrityError):
                continue


        if imported_count > 0:
            try:
                from backend.app.config.database import db
                db.execute_sql(
                    "SELECT setval(pg_get_serial_sequence('users', 'id'), "
                    "(SELECT MAX(id) FROM users))"
                )
            except Exception:
                pass  # Non-fatal: will retry on next INSERT failure

        return imported_count
