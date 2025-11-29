from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError

from core.models import User, Wallet
from .exceptions import InsufficientFundsException
from .repositories import WalletRepository, WalletTransactionRepository

# ======== Wallet Service ======== #
class WalletDomainService:
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
            return Decimal(0)
        return wallet.decimal

    @transaction.atomic
    def deposit(self, user: User, amount: Decimal, description: str = "شارژ کیف پول"):
        """
        افزایش موجودی (واریز)
        """
        
        # ===== دریافت یا ایجاد  کیف پول کاربر ===== #
        wallet = self._wallet_repo.get_locked_wallet(user)
    
        # ===== افزودن مقدار ===== #
        new_balance = wallet.decimal + amount
        
        # ==== به‌روزرسانی کیف پول ===== #
        self._wallet_repo.update(wallet, {"decimal": new_balance})
        
        # ===== ثبت تراکنش ===== #
        self._transaction_repo.create_transaction(
            user=user,
            trans_type="1",
            amount=amount,
            balance_after=new_balance
        )
        return wallet
    
    @transaction.atomic
    def debit(self, user: User, amount: Decimal) -> Wallet:
        """
        مبلغی را از کیف پول کاربر کسر کرده و یک تراکنش ثبت می‌کند.
        این عملیات به صورت اتمیک انجام می‌شود.
        """
        
        if amount <= 0:
            raise ValidationError("مبلغ کسر شده باید مثبت باشد.")
        
        # ===== استفاده از select for update برای جلوگیری از شرایط رقابتی ===== #
        wallet = self._wallet_repo.get_locked_wallet(user)

        #  ===== بررسی مقدار ===== #
        if wallet.decimal < amount:
            raise InsufficientFundsException(f"موجودی کافی نیست. موجودی فعلی: {wallet.decimal}")
        
        # ===== تعیین مقدار جدید ===== #
        new_balance = wallet.decimal - amount
        self._wallet_repo.update(wallet, {"decimal": new_balance})
        
        # ===== افزودن تراکنش ===== #
        self._transaction_repo.create_transaction(
            user=user,
            trans_type="2",
            amount=amount,
            amount_after=new_balance,
        )
        
        return wallet
