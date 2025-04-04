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

class InvalidTokenError(APIException):
    code = 401
    description = "Invalid authentication token"
    
class InvalidPinError(APIException):
    code = 401
    description = "Invalid PIN"

class ForbiddenError(APIException):
    code = 403
    def __init__(self, action="perform this action"):
        self.description = f"You don't have permission to {action}"

#business logic errors

class NotFoundError(APIException):
    code = 404
    def __init__(self, resource_name="Resource"):
        self.description = f"{resource_name} not found"
        super().__init__(description=self.description)

class RetryExceededError(APIException):
    code = 429  # Too Many Requests
    description = "Maximum retry attempts exceeded"

class BusinessRuleViolation(APIException):
    code = 400
    description = "Business rule violation"

class InvalidAccountError(APIException):
    code = 400
    description = "Invalid account"
    
class SecurityValidationError(APIException):
    code = 400
    description = "Security validation failed"
    
# class AccountLockedError(APIException):
#     code = 423
    # def __init__(self, lock_duration=15):
#         self.description = f"Account temporarily locked. Try again in {lock_duration} minutes"
#         self.lock_duration = lock_duration

#custom exceptions
class InsufficientBalanceException(APIException):
    code = 409  # Conflict
    def __init__(self, account_id: int, balance: float):
        super().__init__(f"Account {account_id} has insufficient balance: {balance}")
        self.account_id = account_id
        self.balance = balance

class ConcurrentUpdateError(APIException):
    code = 409
    description = "Resource modified by another request"

#system error
class TransactionFailedError(APIException):
    code = 500
    description = "Transaction processing failed"

