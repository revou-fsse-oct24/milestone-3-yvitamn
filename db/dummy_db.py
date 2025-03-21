from uuid import uuid4
from datetime import datetime
# from .database import Database

class DummyDB: #(Database)
    # def __init__(self):
    #     self.reset()
    _instance = None  # Class-level variable to store singleton instance
    
    def __new__(cls):
        if not cls._instance: # First instantiation
            cls._instance = super().__new__(cls) # Create new instance
            cls._instance.reset() # Initialize collections
        return cls._instance
        
    def reset(self):
        self.users = {}
        self.accounts = {}
        self.transactions = {}

dummy_db_instance = DummyDB()