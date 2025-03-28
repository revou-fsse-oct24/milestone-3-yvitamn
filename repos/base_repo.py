
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
            raise ValueError("Entity missing ID")
            
        if not entity.id:  
            entity.id = str(uuid.uuid4())
            
        if entity.id in self.collection:
            raise ValueError(f"{self.model.__name__} {entity.id} already exists")
        
        # Store in collection 
        self.collection[entity.id] = entity
        
        # Auto-index all predefined fields
        if self.collection_name in self.db._indexes:
            for field in self.db._indexes[self.collection_name]:
                value = getattr(entity, field, None)
                if value is not None:
                    self.db.add_to_index(
                        self.collection_name,
                        field,
                        value,
                        entity.id
                    )
             
        return entity

    def find_by_id(self, entity_id: str) -> Optional[T]:
        return self.collection.get(entity_id)

    def find_all(self, page: int = 1, per_page: int = 10) -> list[T]:
        all_items = list(self.collection.values())
        start = (page - 1) * per_page
        end = start + per_page
        return all_items[start:end]
    
    def update(self, entity: T) -> T:
        old_entity = self.find_by_id(entity.id)
        if not old_entity:
            raise ValueError("Entity does not exist")

        # Remove old indexes
        if self.collection_name in self.db._indexes:
            for field in self.db._indexes[self.collection_name]:
                old_value = getattr(old_entity, field, None)
                if old_value is not None:
                    self.db.remove_from_index(
                        self.collection_name,
                        field,
                        old_value,
                        entity.id
                    )

        # Update entity
        self.collection[entity.id] = entity

        # Add new indexes
        if self.collection_name in self.db._indexes:
            for field in self.db._indexes[self.collection_name]:
                new_value = getattr(entity, field, None)
                if new_value is not None:
                    self.db.add_to_index(
                        self.collection_name,
                        field,
                        new_value,
                        entity.id
                    )
        return entity


    def delete(self, entity_id: str) -> bool:
        entity = self.collection.pop(entity_id, None)
        if entity and self.collection_name in self.db._indexes:
            for field in self.db._indexes[self.collection_name]:
                value = getattr(entity, field, None)
                if value is not None:
                    self.db.remove_from_index(
                        self.collection_name,
                        field,
                        value,
                        entity_id
                    )
        return entity is not None
     
     
     
    def atomic_update(self, entity_id: str, update_fn: Callable[[T], T]) -> T:
        entity = self.find_by_id(entity_id)
        if not entity:
            raise ValueError("Entity not found")
        updated_entity = update_fn(entity)
        return self.update(updated_entity)