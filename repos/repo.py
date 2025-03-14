from db.dummy_db import dummy_db

class UserRepository:
    @staticmethod
    def create_user(user):
        dummy_db.users[user.id] = user
        return user
    
    @staticmethod
    def find_by_username(username):
        return next((u for u in dummy_db.users.values() if u.username == username), None)

class AccountRepository:
    @staticmethod
    def create_account(account):
        dummy_db.accounts[account.id] = account
        return account
    
    @staticmethod
    def find_by_user(user_id):
        return [acc for acc in dummy_db.accounts.values() if acc.user_id == user_id]

class TransactionRepository:
    @staticmethod
    def create_transaction(transaction):
        dummy_db.transactions[transaction.id] = transaction
        return transaction
    
    @staticmethod
    def find_by_user(user_id):
        user_accounts = [acc.id for acc in dummy_db.accounts.values() if acc.user_id == user_id]
        return [t for t in dummy_db.transactions.values() 
                if t.from_account_id in user_accounts 
                or t.to_account_id in user_accounts]