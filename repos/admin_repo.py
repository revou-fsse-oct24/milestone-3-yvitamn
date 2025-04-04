























#undoing a previous transaction
    # def revert_transaction(self, transaction_id: str) -> Transaction:
    #     transaction = self.find_by_id(transaction_id)
    #     if not transaction:
    #         raise NotFoundError("Transaction not found")
            
    #     account_repo = AccountRepository()
        
    #     # Reverse the transaction
    #     if transaction.from_account_id:
    #         account_repo.update_balance(
    #             transaction.from_account_id,
    #             transaction.amount
    #         )
    #     if transaction.to_account_id:
    #         account_repo.update_balance(
    #             transaction.to_account_id,
    #             -transaction.amount
    #         )
            
    #     transaction.status = "reverted"
    #     return transaction