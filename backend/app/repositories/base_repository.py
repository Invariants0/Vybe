from typing import Any, Dict, Generic, List, Optional, TypeVar

from peewee import DoesNotExist, IntegrityError

from backend.app.config.database import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseRepository(Generic[T]):
    def __init__(self, model_class: type[T]):
        self.model = model_class

    def create(self, **kwargs: Any) -> T:
        """Create and return instance."""
        return self.model.create(**kwargs)

    def get_by_id(self, entity_id: int) -> Optional[T]:
        """Fetch entity by primary key."""
        try:
            return self.model.get_by_id(entity_id)
        except DoesNotExist:
            return None

    def get_one(self, **filters: Any) -> Optional[T]:
        """Fetch exact match for filters."""
        try:
            return self.model.get(**filters)
        except DoesNotExist:
            return None

    def get_all(self, skip: int = 0, limit: int = 100, order_by: Any = None, **filters: Any) -> List[T]:
        """Fetch multiple entities with simple pagination and filtering."""
        query = self.model.select()
        if order_by is not None:
            query = query.order_by(order_by)
        for key, value in filters.items():
            query = query.where(getattr(self.model, key) == value)
        return list(query.offset(skip).limit(limit))

    def update(self, entity_id: int, **updates: Any) -> Optional[T]:
        """Update entity fields and return updated instance."""
        obj = self.get_by_id(entity_id)
        if not obj:
            return None

        # Determine fields to actually save
        to_save = []
        for key, value in updates.items():
            setattr(obj, key, value)
            to_save.append(getattr(self.model, key))
        if to_save:
            obj.save(only=to_save)
        return obj

    def delete(self, entity_id: int) -> bool:
        """Delete entity by primary key."""
        return self.model.delete_by_id(entity_id) > 0

    def exists(self, **filters: Any) -> bool:
        """Check if an entity exists."""
        query = self.model.select()
        for key, value in filters.items():
            query = query.where(getattr(self.model, key) == value)
        return query.exists()
