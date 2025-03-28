from werkzeug.exceptions import HTTPException

class APIException(HTTPException):
    """Base exception class for all API errors"""
    def __init__(self, description=None, code=None):
        super().__init__(description=description)
        if code is not None:
            self.code = code
            
# ========== Authentication & Authorization Errors (4xx) ==========
class UnauthorizedError(APIException):
    code = 401
    description = "Authentication required"
    
class InvalidCredentialsError(APIException):
    code = 401
    description = "Invalid credentials"
    
class NotFoundError(APIException):
    code = 404
    description = "Resource not found"    

class InvalidTokenError(APIException):
    code = 401
    description = "Invalid authentication token"
    
class InvalidPinError(APIException):
    code = 401
    description = "Invalid PIN"

class ForbiddenError(APIException):
    code = 403
    description = "Access forbidden"

#business logic errors

class NotFoundError(APIException):
    code = 404
    def __init__(self, resource_name="Resource"):
        self.description = f"{resource_name} not found"

class RetryExceededError(APIException):
    code = 429  # Too Many Requests
    description = "Maximum retry attempts exceeded"

class BusinessRuleViolation(APIException):
    code = 400
    description = "Business rule violation"

class InvalidAccountError(APIException):
    code = 400
    description = "Invalid account"

# System errors
class TransactionFailedError(APIException):
    code = 500
    description = "Transaction processing failed"

#custom exceptions
class InsufficientBalanceException(APIException):
    code = 409  # Conflict
    def __init__(self, account_id: int, balance: float):
        super().__init__(f"Account {account_id} has insufficient balance: {balance}")
        self.account_id = account_id
        self.balance = balance

#system error
class TransactionFailedError(APIException):
    code = 500
    description = "Transaction processing failed"

# class AccountLockedError(APIException):
#     code = 403
#     def __init__(self, lock_duration=15):
#         self.description = f"Account locked. Try again in {lock_duration} minutes"
#         self.lock_duration = lock_duration
