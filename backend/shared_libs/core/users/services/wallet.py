from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError

from ..models import User, Wallet, WalletTransaction
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
            return wallet.decimal
        except WalletNotFoundException:
            return Decimal(0)

    @transaction.atomic
    def deposit(self, user: User, amount: Decimal):
        """
        افزایش موجودی (واریز)
        """
        
        # ===== دریافت یا ایجاد کیف پول کاربر (با قفل) ===== #
        wallet = Wallet.objects.get_locked_wallet(user)
    
        # ===== افزودن مقدار ===== #
        new_balance = wallet.decimal + amount
        
        # ==== به‌روزرسانی کیف پول ===== #
        wallet.decimal = new_balance
        wallet.save()
        
        # ===== ثبت تراکنش ===== #
        WalletTransaction.objects.create_transaction(
            user=user,
            trans_type="1",
            amount=amount,
            amount_after=new_balance
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
        wallet = Wallet.objects.get_locked_wallet(user)

        #  ===== بررسی مقدار ===== #
        if wallet.decimal < amount:
            raise InsufficientFundsException(f"موجودی کافی نیست. موجودی فعلی: {wallet.decimal}")
        
        # ===== تعیین مقدار جدید ===== #
        new_balance = wallet.decimal - amount
        
        wallet.decimal = new_balance
        wallet.save()
        
        # ===== افزودن تراکنش ===== #
        WalletTransaction.objects.create_transaction(
            user=user,
            trans_type="2",
            amount=amount,
            amount_after=new_balance,
        )
        
        return wallet
