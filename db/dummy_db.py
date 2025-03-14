from uuid import uuid4
from datetime import datetime

class DummyDB:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.users = {}
        self.accounts = {}
        self.transactions = {}

dummy_db = DummyDB()