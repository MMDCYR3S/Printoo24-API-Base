from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError

from core.models import User
from core.infrastructure.messages import msg_provider
from ..models import Wallet, WalletTransaction
from ..exceptions import InsufficientFundsException, WalletNotFoundException

# ======== Wallet Service ======== #
class WalletService:
    """
    سرویس کیف پول (جایگزین WalletDomainService)
    """

    def get_user_balance(self, user: User) -> Decimal:
        """ موجودی کیف پول کاربر را برمی‌گرداند. """
        try:
            wallet = Wallet.objects.get_by_user(user)
            return wallet.balance
        except WalletNotFoundException:
            return Decimal(0)

    @transaction.atomic
    def deposit(self, user: User, amount: Decimal):
        """
        افزایش موجودی (واریز)
        """
        
        # ===== دریافت یا ایجاد کیف پول کاربر (با قفل) ===== #
        wallet = Wallet.objects.get_locked_wallet(user)

        # ==== به‌روزرسانی کیف پول ===== #
        wallet.deposit(amount)
        wallet.save()
        
        # ===== ثبت تراکنش ===== #
        WalletTransaction.objects.create_transaction(
            user=user,
            trans_type="2",
            amount=amount,
            amount_after=wallet.balance
        )
        return wallet
    
    @transaction.atomic
    def debit(self, user: User, amount: Decimal) -> Wallet:
        """
        مبلغی را از کیف پول کاربر کسر کرده و یک تراکنش ثبت می‌کند.
        این عملیات به صورت اتمیک انجام می‌شود.
        """
        
        if amount <= 0:
            raise ValidationError(msg_provider.get("wallet.E3001"))
        
        # ===== استفاده از select for update برای جلوگیری از شرایط رقابتی ===== #
        wallet = Wallet.objects.get_locked_wallet(user)

        #  ===== بررسی مقدار ===== #
        if wallet.balance < amount:
            pass
        
        # ===== تعیین مقدار جدید ===== #
        wallet.withdraw(amount) 
        wallet.save()
        
        # ===== افزودن تراکنش ===== #
        WalletTransaction.objects.create_transaction(
            user=user,
            trans_type="6",
            amount=amount,
            amount_after=wallet.balance
        )
        return wallet


class WalletTransactionService:
    """ سرویس تراکنش‌های کیف پول """
    
    def get_history_by_user(self, user_id: int):
        return WalletTransaction.objects.get_history_by_user(user_id)
