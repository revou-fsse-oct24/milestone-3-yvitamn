from typing import Dict, Optional, Type, Generic, TypeVar
# from abc import ABC, abstractmethod
import uuid
from db.dummy_db import dummy_db_instance

T = TypeVar('T')

# class BaseRepository(Generic[T]):
#     def __init__(self, model: Type[T]):
#         self.model = model
    
#     @abstractmethod    
#     def create(self, entity: T) -> T:
#         raise NotImplementedError
    
#     @abstractmethod
#     def update(self, entity: T) -> T:
#         raise NotImplementedError
    
#     @abstractmethod
#     def delete(self, entity_id: str) -> bool:
#         raise NotImplementedError
    
#     @abstractmethod
#     def find_by_id(self, entity_id: str) -> Optional[T]:
#         raise NotImplementedError

print(type(dummy_db_instance))
print(dummy_db_instance.users)

class DummyBaseRepository(Generic[T]):
    def __init__(self, model: Type[T], collection_name: str):
        super().__init__()
        # from db.dummy_db import dummy_db_instance
        # self.collection = getattr(dummy_db_instance, collection_name)
        self.model = model
        self.db = dummy_db_instance  # Reference the shared DummyDB instance
        self.collection_name = collection_name

    @property
    def collection(self) -> Dict[str, T]:
        """Access the appropriate collection in DummyDB"""
        return getattr(self.db, self.collection_name)
        
    def create(self, entity: T) -> T:
        """Auto-generate ID if missing, prevent duplicates"""
        if not hasattr(entity, 'id') or not entity.id:
            entity.id = str(uuid.uuid4())
            
        if entity.id in self.collection:
            raise ValueError(f"{self.model.__name__} {entity.id} already exists")
            
        self.collection[entity.id] = entity
        return entity

    def find_by_id(self, entity_id: str) -> Optional[T]:
        return self.collection.get(entity_id)

    def find_all(self) -> list[T]:
        return list(self.collection.values())

    def update(self, entity: T) -> T:
        self.collection[entity.id] = entity
        return entity

    def delete(self, entity_id: str) -> bool:
        if entity_id in self.collection:
            del self.collection[entity_id]
            return True
        return False