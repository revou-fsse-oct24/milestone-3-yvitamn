from uuid import uuid4
from datetime import datetime
# from .database import Database

class DummyDB: #(Database)
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.users = {}
        self.accounts = {}
        self.transactions = {}

dummy_db_instance = DummyDB()