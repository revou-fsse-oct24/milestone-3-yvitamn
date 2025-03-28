from typing import Any
from uuid import uuid4
from datetime import datetime
# from .database import Database
from threading import Lock

class DummyDB: #(Database)
    # def __init__(self):
    #     self.reset()
    _instance = None  # Class-level variable to store singleton instance
    _lock: Lock = Lock() # This is a threading lock for thread-safety
    
    def __new__(cls):
        with cls._lock:
            if not cls._instance: # First instantiation
                cls._instance = super().__new__(cls) # Create new instance
                cls._instance.reset() # Initialize collections
            return cls._instance
        
    def reset(self):
        self.users = {}
        self.accounts = {}
        self.transactions = {}
        self._indexes = {
            'users': {'email': {}},
            'accounts': {'user_id': {}}
        }

    def add_to_index(self, collection: str, field: str, value: Any, entity_id: str):
        if collection in self._indexes and field in self._indexes[collection]:
            index = self._indexes[collection][field]
            if value not in index:
                index[value] = set()
            index[value].add(entity_id)
            
    def remove_from_index(self, collection: str, field: str, value: Any, entity_id: str):
        if collection in self._indexes and field in self._indexes[collection]:
            index = self._indexes[collection][field]
            if value in index and entity_id in index[value]:
                index[value].remove(entity_id)

#singleton instance
dummy_db_instance = DummyDB()