from typing import Optional, Type, Generic, TypeVar

T = TypeVar('T')

class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model
        
    def create(self, entity: T) -> T:
        raise NotImplementedError
    
    def update(self, entity: T) -> T:
        raise NotImplementedError
    
    def delete(self, entity_id: str) -> bool:
        raise NotImplementedError
    
    def find_by_id(self, entity_id: str) -> Optional[T]:
        raise NotImplementedError

# Example implementation for DummyDB
class DummyBaseRepository(BaseRepository):
    def __init__(self, model, collection_name: str):
        super().__init__(model)
        from db.dummy_db import dummy_db
        self.collection = getattr(dummy_db, collection_name)
        
    def create(self, entity: T) -> T:
        self.collection[entity.id] = entity
        return entity
    
    def find_by_id(self, entity_id: str) -> Optional[T]:
        return self.collection.get(entity_id)
    
    def update(self, entity: T) -> T:
        self.collection[entity.id] = entity
        return entity
    
    def delete(self, entity_id: str) -> bool:
        if entity_id in self.collection:
            del self.collection[entity_id]
            return True
        return False