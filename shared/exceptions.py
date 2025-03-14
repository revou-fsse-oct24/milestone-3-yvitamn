from werkzeug.exceptions import HTTPException

class InvalidPinError(HTTPException):
    code = 401
    description = "Invalid PIN"

class RetryExceededError(HTTPException):
    code = 403
    description = "Maximum retry attempts exceeded"

class BusinessRuleViolation(HTTPException):
    code = 400
    description = "Business rule violation"

class NotFoundError(HTTPException):
    code = 404
    description = "Resource not found"

class InvalidAccountError(HTTPException):
    code = 400
    description = "Invalid account"

class TransactionFailedError(HTTPException):
    code = 500
    description = "Transaction processing failed"


#custom 
class InsufficientBalanceException(Exception):
    def __init__(self, account_id: int, balance: float):
        super().__init__(f"Account {account_id} has insufficient balance: {balance}")
        self.account_id = account_id
        self.balance = balance

# class AccountLockedError(Exception):
#     def __init__(self, email: str, lock_time: int):
#         super().__init__(f"Account for {email} is locked")
#         self.email = email
#         self.lock_time = lock_time  # customize how long

# class TransactionRetryException(Exception):
#     def __init__(self, transaction_id: str):
#         super().__init__(f"Transaction {transaction_id} retry limit exceeded")
#         self.transaction_id = transaction_id
