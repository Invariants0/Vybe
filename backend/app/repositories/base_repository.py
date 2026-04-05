from typing import Any, Generic, List, Optional, TypeVar

from peewee import DoesNotExist

from backend.app.config.database import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseRepository(Generic[T]):
    def __init__(self, model_class: type[T]):
        self.model = model_class

    def create(self, **kwargs: Any) -> T:
        return self.model.create(**kwargs)

    def get_by_id(self, entity_id: int) -> Optional[T]:
        try:
            return self.model.get_by_id(entity_id)
        except DoesNotExist:
            return None

    def get_one(self, **filters: Any) -> Optional[T]:
        try:
            return self.model.get(**filters)
        except DoesNotExist:
            return None

    def get_all(
        self, skip: int = 0, limit: int = 100, order_by: Any = None, **filters: Any
    ) -> List[T]:
        query = self.model.select()
        if order_by is not None:
            query = query.order_by(order_by)
        for key, value in filters.items():
            query = query.where(getattr(self.model, key) == value)
        return list(query.offset(skip).limit(limit))

    def update(self, entity_id: int, **updates: Any) -> Optional[T]:
        obj = self.get_by_id(entity_id)
        if not obj:
            return None

        to_save = []
        for key, value in updates.items():
            setattr(obj, key, value)
            to_save.append(getattr(self.model, key))
        if to_save:
            obj.save(only=to_save)
        return obj

    def delete(self, entity_id: int) -> bool:
        return self.model.delete_by_id(entity_id) > 0  # delete entity by primary key

    def exists(self, **filters: Any) -> bool:
        query = self.model.select()
        for key, value in filters.items():
            query = query.where(getattr(self.model, key) == value)
        return query.exists()  # check if an entity exists
