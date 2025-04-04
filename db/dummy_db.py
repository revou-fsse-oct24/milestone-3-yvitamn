import secrets
from typing import Any, Dict
from uuid import uuid4
from datetime import datetime
# from .database import Database
from threading import Lock


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
                cls._instance.reset() # Initialize collections
            return cls._instance
        
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
        """index management with auto-creation"""  
        """Thread-safe index addition with validation"""
        with AtomicOperation(self):  
            if collection not in self._indexes:
                raise ValueError(f"Collection {collection} not registered for indexing")
            
            # Create collection if not exists
            if collection not in self._indexes[collection]:
                raise ValueError(f"Field {field} not indexed in {collection}")
                # self._indexes[collection] = {}   
                
            # Create field index if not exists         
            # if field not in self._indexes[collection]:
            #     self._indexes[collection][field] = {}
                
            index = self._indexes[collection][field]
            if value not in index:
                    index[value] = set()
            index[value].add(entity_id)
            
    def remove_from_index(self, 
                          collection: str, 
                          field: str, 
                          value: Any, 
                          entity_id: str):
        """Thread-safe index removal with safety checks"""
        with AtomicOperation(self):
            try:
                if (collection in self._indexes and 
                field in self._indexes[collection] and
                value in self._indexes[collection][field] and
                 entity_id in self._indexes[collection][field][value]):
                
                    self._indexes[collection][field][value].remove(entity_id)
                    if not self._indexes[collection][field][value]:
                        del self._indexes[collection][field][value]    
            except KeyError:
                pass #handle missing entries

        
        def generate_account_number(self) -> str:
            """Generate secure account numbers"""
            with AtomicOperation(self):
                return f"ACCT-{secrets.token_hex(6)}"  # 12-character random
        
        
#singleton initialization
dummy_db_instance = DummyDB()