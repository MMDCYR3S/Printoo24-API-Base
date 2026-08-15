from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError

from core.models import User
from core.infrastructure.messages import msg_provider
from ..models import Wallet, WalletTransaction
from ..exceptions import InsufficientFundsException, WalletNotFoundException


class WalletService:
    """
    سرویس کیف پول با پشتیبانی از عملیات اتمیک و ثبت دقیق تراکنش‌ها
    """

    def get_user_balance(self, user: User):
        """
        موجودی کیف پول کاربر را برمی‌گرداند.
        """
        try:
            return Wallet.objects.get_by_user(user)
        except WalletNotFoundException:
            return None

    @transaction.atomic
    def deposit(
        self,
        user: User,
        amount: Decimal,
        description: str = "",
        created_by: User = None,
        order=None,
        payment=None,
        invoice=None,
    ):
        """
        افزایش موجودی (واریز)
        """
        if amount <= 0:
            raise ValidationError(msg_provider.get("wallet.E3001"))

        wallet = Wallet.objects.get_locked_wallet(user)

        balance_before = wallet.balance
        wallet.deposit(amount)
        wallet.total_deposits = (wallet.total_deposits or 0) + amount
        wallet.save()

        WalletTransaction.objects.create_transaction(
            wallet=wallet,
            user=user,
            transaction_type=WalletTransaction.Type.DEPOSIT,
            amount=amount,
            balance_before=balance_before,
            balance_after=wallet.balance,
            description=description or "واریز به کیف پول",
            created_by=created_by,
            order=order,
            payment=payment,
            invoice=invoice,
        )
        return wallet

    @transaction.atomic
    def debit(
        self,
        user: User,
        amount: Decimal,
        description: str = "",
        created_by: User = None,
        order=None,
        payment=None,
        invoice=None,
    ):
        """
        کسر مبلغ از کیف پول (برداشت یا پرداخت)
        """
        if amount <= 0:
            raise ValidationError(msg_provider.get("wallet.E3001"))

        wallet = Wallet.objects.get_locked_wallet(user)

        balance_before = wallet.balance
        wallet.withdraw(amount)
        wallet.total_withdrawals = (wallet.total_withdrawals or 0) + amount
        wallet.save()

        WalletTransaction.objects.create_transaction(
            wallet=wallet,
            user=user,
            transaction_type=WalletTransaction.Type.WITHDRAWAL,
            amount=amount,
            balance_before=balance_before,
            balance_after=wallet.balance,
            description=description or "برداشت از کیف پول",
            created_by=created_by,
            order=order,
            payment=payment,
            invoice=invoice,
        )
        return wallet


class WalletTransactionService:
    """
    سرویس تراکنش‌های کیف پول
    """

    def get_history_by_user(self, user_id: int):
        return WalletTransaction.objects.get_history_by_user(user_id)