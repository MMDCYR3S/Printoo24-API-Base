from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from core.common.wallet import WalletRepository, WalletTransactionRepository

# ===== Wallet Service ===== #
class WalletService:
    def __init__(self):
        self._wallet_repo = WalletRepository()
        self._trans_repo = WalletTransactionRepository()

    def get_wallet_balance(self, user_id: int):
        """نمایش موجودی فعلی"""
        wallet = self._wallet_repo.get_by_user(user_id)
        return wallet
    
    def get_transaction_history(self, user_id: int):
        """نمایش تاریخچه"""
        return self._trans_repo.get_history_by_user(user_id)
