


from shared.exceptions import *


class AdminService:
      
    def list_users(self, requester_id: str) -> list:
        """Admin-only user listing with security check"""
        requester = self.user_repo.find_by_id(requester_id)
        if not requester or requester.role != 'admin':
            raise ForbiddenError("Admin privileges required")
            
        return [u.to_dict() for u in self.repo.find_all()]
    
    # def revert_transaction(self, admin_id: str, txn_id: str):
        # Verify transaction exists
        # Check transaction reversibility
        # Create reverse transaction
        # Update balances
        
    # def update_user(self, admin_id: str, target_id: str, update_data: dict) -> User:
        # Verify admin privileges
        # Validate role changes
        # Prevent self-modification of admin status
        # Update user
