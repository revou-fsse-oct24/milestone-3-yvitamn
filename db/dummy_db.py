from typing import Any, Dict
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
        self.users = Dict[str, Any] = {}
        self.accounts = Dict[str, Any] = {}
        self.transactions = Dict[str, Any] = {}
        
        # Initialize all indexes
        self._indexes = {
            'users': {
                'email': {},
                'username': {},
                'token': {}
            },
            'accounts': {
                'user_id': {},
                'account_number': {}
            },
            'transactions': {
                'transaction_id': {},
                'from_account': {},
                'to_account': {},
                'type': {},
                'status': {},
                'user_id': {}
            }
        }

    #Universal index management method
    def add_to_index(self, 
                     collection: str, 
                     field: str, 
                     value: Any, 
                     entity_id: str):    
        """index management with auto-creation"""   
        # Create collection if not exists
        if collection in self._indexes:
            self._indexes[collection] = {}   
            
        # Create field index if not exists         
        if field not in self._indexes[collection]:
            self._indexes[collection][field] = {}
            
        index = self._indexes[collection][field]
        if value not in index:
                index[value] = set()
        index[value].add(entity_id)
            
    def remove_from_index(self, 
                          collection: str, 
                          field: str, 
                          value: Any, 
                          entity_id: str):
        if collection in self._indexes and field in self._indexes[collection]:
            index = self._indexes[collection][field]
            if value in index and entity_id in index[value]:
                index[value].remove(entity_id)
                if not index[value]:  # Cleanup empty sets
                    del index[value]

#singleton instance
dummy_db_instance = DummyDB()