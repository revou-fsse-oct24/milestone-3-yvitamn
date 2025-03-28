
from abc import ABC, abstractmethod
from typing import Callable, Dict, Optional, Type, Generic, TypeVar, Any

import uuid
from uuid import UUID
from db.dummy_db import dummy_db_instance
from models.user_model import User

T = TypeVar('T')

class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T], collection_name: str):
        self.model = model
        self.collection_name = collection_name
    
    @abstractmethod
    def create(self, entity_data: dict) -> T:
        pass

    @abstractmethod
    def update(self, entity: T) -> T:
        pass

    @abstractmethod
    def delete(self, entity_id: str) -> bool:
        pass

    @abstractmethod
    def find_by_id(self, entity_id: str) -> Optional[T]:
        pass
    
    


# print(type(dummy_db_instance))
# print(dummy_db_instance.users)

class DummyBaseRepository(BaseRepository):
    def __init__(self, model: Type[T], collection_name: str):
        super().__init__(model, collection_name)
        self.db = dummy_db_instance  
        
    @property
    def collection(self) -> Dict[str, T]:
        """Access the appropriate collection in DummyDB"""
        return getattr(self.db, self.collection_name)
        
    def create(self, entity: T) -> T:
        """Create users with index management"""
        #base creation logic
        if not hasattr(entity, 'id'):
            raise ValueError("Entity must have 'id' attribute")
            
        if not entity.id:  
            entity.id = str(uuid.uuid4())
            
        if entity.id in self.collection:
            raise ValueError(f"{self.model.__name__} {entity.id} already exists")
            
        self.collection[entity.id] = entity
        
        # Update indexes after successful creation
        self.db.add_to_index('users', 'email', entity.email, entity.id)
        self.db.add_to_index('users', 'username', entity.username, entity.id)
             
        return entity

    def find_by_id(self, entity_id: str) -> Optional[T]:
        return self.collection.get(entity_id)

    def find_all(self, page: int = 1, per_page: int = 10) -> list[T]:
        all_items = list(self.collection.values())
        start = (page - 1) * per_page
        end = start + per_page
        return all_items[start:end]
    
    def update(self, entity: T) -> T:
        if entity.id not in self.collection:
            raise ValueError("Entity does not exist")
        self.collection[entity.id] = entity
        return entity

    def delete(self, entity_id: str) -> bool:
         return self.collection.pop(entity_id, None) is not None
     
     
     
    def atomic_update(self, entity_id: str, update_fn: Callable[[T], T]) -> T:
        entity = self.find_by_id(entity_id)
        if not entity:
            raise ValueError("Entity not found")
        updated_entity = update_fn(entity)
        return self.update(updated_entity)