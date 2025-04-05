import secrets
from typing import Any, Dict
from uuid import uuid4
from datetime import datetime
# from .database import Database
from threading import Lock

from marshmallow import ValidationError


class AtomicOperation:
    """Context manager for atomic database operations"""
    def __init__(self, db):
        self.db = db
        
    def __enter__(self):
        self.db.data_lock.acquire()
        return self  # Return value available to 'as' clause
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.data_lock.release()
        # Handle exceptions if needed
        return False  # Let exceptions propagate
    
    
class DummyDB: #(Database)
    _instance = None  # Class-level variable to store singleton instance
    _class_lock = Lock() # This is a threading lock for thread-safety
    
    def __new__(cls):
        with cls._class_lock:
            if not cls._instance: # First instantiation
                cls._instance = super().__new__(cls) # Create new instance
                
                # Initialize instance variables in __new__ since we're bypassing __init__
                cls._instance.data_lock = Lock()
                cls.collection_locks = {
                    'users': Lock(),
                    'accounts': Lock(),
                    'transactions': Lock()
                }
                cls._instance.reset() # Initialize collections
            return cls._instance
    
    def get_collection_lock(self, collection: str) -> Lock:
        return self.collection_locks.get(collection, self.data_lock)
    
    def reset(self):
        """Initialize all data structures with instance lock"""
        with AtomicOperation(self): #use context manager
            self.users: Dict[str, Any] = {}
            self.accounts: Dict[str, Any] = {}
            self.transactions: Dict[str, Any] = {}
        
            # Initialize all indexes
            self._indexes = {
                'users': {
                    'email': {}, # For login/unique check
                    'username': {}, # For login/unique check
                    'token': {} # For auth token validation
                },
                'accounts': {
                    'user_id': {}, # Auto-indexed
                    'account_number': {}, # Auto-indexed
                    'balance': {}      # For overdraft prevention checks
                },
                'transactions': {
                    'transaction_id': {},
                    'from_account': {}, # Auto-indexed
                    'to_account': {}, # Auto-indexed
                    'type': {},
                    'amount': {},
                    'created_at': {},
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
        """Thread-safe index addition with auto-creation"""
        with AtomicOperation(self):  
            # Create collection if not exists
            if collection not in self._indexes:
                # raise ValueError(f"Collection {collection} not registered for indexing")
                 self._indexes[collection] = {}
                     
            if field not in self._indexes[collection]:
                self._indexes[collection][field] = {}
            
            # Get reference to the index
            index = self._indexes[collection][field]
            
            # Enforce uniqueness for specific fields
            if collection == 'users' and field in ['email', 'username']:
                if value in index and len(index[value]) > 0:
                    raise ValidationError(f"{field} {value} already exists")    
                
            if value not in index:
                    index[value] = set()
            index[value].add(entity_id)
            
    def remove_from_index(self, 
                          collection: str, 
                          field: str, 
                          value: Any, 
                          entity_id: str):
        """Thread-safe index removal with auto-cleanup"""
        with AtomicOperation(self):
            try:
                if collection in self._indexes:
                    collection_index = self._indexes[collection]
                    if field in collection_index:
                        field_index = collection_index[field]
                        if value in field_index and entity_id in field_index[value]:
                            field_index[value].remove(entity_id) # Clean up empty indexes   
                            if not field_index[value]:
                                del field_index[value]
                   
            except KeyError:
                pass #handle missing entries

    def auto_index(self, entity_type: str, entity_id: str, data: dict, unique_fields: list = []):
        """Automatically index fields marked for a collection"""
        with AtomicOperation(self):  # Thread-safe
            for field in self._indexes.get(entity_type, {}):
                value = data.get(field)
                if value is not None:
                    # Check uniqueness before adding
                    if field in unique_fields:
                        existing = self._indexes[entity_type][field].get(value, set())
                        if existing:
                            raise ValidationError(f"{field} must be unique")
                    self.add_to_index(entity_type, field, value, entity_id)


    def find_by(self, collection: str, field: str, value: Any) -> list:
        """Generic indexed lookup"""
        with AtomicOperation(self):  # Thread-safe read
            if collection not in self._indexes:
                raise ValueError(f"Collection {collection} not indexed")
            
            if field not in self._indexes[collection]:
                raise ValueError(f"Field {field} not indexed in {collection}")
            
            entity_ids = self._indexes[collection][field].get(value, set())
            return [self.__dict__[collection][_id] for _id in entity_ids]

    
    def generate_account_number(self) -> str:
        """Generate secure account numbers"""
        with AtomicOperation(self):
            return f"ACCT-{secrets.token_hex(6)}"  # 12-character random
        
        
#singleton initialization
dummy_db_instance = DummyDB()