from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError

from core.models import User, Wallet
from .wallet_repo import WalletRepository, WalletTransactionRepository

# ======== Wallet Service ======== #
class WalletService:
    """
    سرویس کیف پول
    """
    def __init__(self):
        self._wallet_repo = WalletRepository()
        self._transaction_repo = WalletTransactionRepository()

    def get_user_balance(self, user: User) -> Decimal:
        """ موجودی کیف پول کاربر را برمی‌گرداند. """
        wallet = self._wallet_repo.get_by_user(user)
        if not wallet:
            raise ValidationError("کیف پول برای این کاربر یافت نشد.")
        return wallet.decimal

    @transaction.atomic
    def debit(self, user: User, amount: Decimal, transaction_type: str) -> Wallet:
        """
        مبلغی را از کیف پول کاربر کسر کرده و یک تراکنش ثبت می‌کند.
        این عملیات به صورت اتمیک انجام می‌شود.
        """
        
        if amount <= 0:
            raise ValidationError("مبلغ کسر شده باید مثبت باشد.")
        # ===== استفاده از select for update برای جلوگیری از شرایط رقابتی ===== #
        wallet = Wallet.objects.select_for_update().get(user=user)

        if wallet.decimal < amount:
            raise ValidationError("موجودی کافی نیست.")
        
        # ===== تعیین مقدار جدید ===== #
        new_balance = wallet.decimal - amount
        self._wallet_repo.update(wallet, {"decimal" : new_balance})
        
        # ===== افزودن تراکنش ===== #
        self._transaction_repo.create_transaction(
            user=user,
            trans_type=transaction_type,
            amount=amount,
            amount_after=new_balance,
        )
        
        return wallet
