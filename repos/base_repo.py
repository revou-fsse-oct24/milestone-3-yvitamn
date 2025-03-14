# repositories/base_repo.py
from typing import Type, Generic, TypeVar

T = TypeVar('T')

class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model
        
    def create(self, entity: T) -> T:
        raise NotImplementedError
    
    def update(self, entity: T) -> T:
        raise NotImplementedError
    
    def delete(self, entity_id: str):
        raise NotImplementedError
    
    def find_by_id(self, entity_id: str) -> T:
        raise NotImplementedError

# Example implementation for DummyDB
class DummyBaseRepository(BaseRepository):
    def __init__(self, model, collection_name):
        super().__init__(model)
        from db.dummy_db import dummy_db
        self.collection = getattr(dummy_db, collection_name)
        
    def create(self, entity):
        self.collection[entity.id] = entity
        return entity
    
    def find_by_id(self, entity_id):
        return self.collection.get(entity_id)