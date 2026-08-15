import logging
from decimal import Decimal
from django.db import transaction
from rest_framework.exceptions import NotFound, ValidationError

from apps.accounts.models import Wallet
from apps.accounts.services import WalletService
from core.users.services import CustomerService
from apps.accounts.exceptions import WalletNotFoundException

logger = logging.getLogger('dashboard.services.wallet')


class WalletDashboardService:
    """
    سرویس مدیریت کیف پول مخصوص داشبورد ادمین.
    """

    def __init__(self):
        self.domain_service = WalletService()
        self.user_repo = CustomerService()

    def get_wallets_queryset(self):
        """
        لیست کیف پول‌ها با بهینه‌سازی (select_related) برمی‌گرداند.
        """
        return (
            Wallet.objects
            .select_related('user__customer_profile')
            .all()
            .order_by('-updated_at')
        )

    @transaction.atomic
    def adjust_balance(
        self,
        user_id: int,
        amount: Decimal,
        action_type: str,
        actor=None,
        description: str = "",
    ) -> Wallet:
        """
        اصلاح موجودی (واریز یا برداشت) توسط ادمین.
        """
        logger.info(
            f"START: Adjust balance for User {user_id}. Amount: {amount}, Type: {action_type}"
        )

        user = self.user_repo.get_customer_by_id(user_id)
        if not user:
            raise NotFound("کاربر مورد نظر یافت نشد.")

        if amount <= 0:
            raise ValidationError("مبلغ باید بزرگتر از صفر باشد.")

        if action_type == 'deposit':
            wallet = self.domain_service.deposit(
                user=user,
                amount=amount,
                description=description or "اصلاح موجودی توسط ادمین",
                created_by=actor,
            )
            logger.info(f"DEPOSIT SUCCESS: User {user_id}, New Balance: {wallet.balance}")

        elif action_type == 'debit':
            wallet = self.domain_service.debit(
                user=user,
                amount=amount,
                description=description or "برداشت توسط ادمین",
                created_by=actor,
            )
            logger.info(f"DEBIT SUCCESS: User {user_id}, New Balance: {wallet.balance}")

        else:
            raise ValidationError("نوع عملیات نامعتبر است.")

        return wallet

    def get_wallet_by_user_id(self, user_id: int) -> Wallet:
        try:
            return Wallet.objects.get(user_id=user_id)
        except Wallet.DoesNotExist:
            raise WalletNotFoundException("کیف پول کاربر یافت نشد.")

    def get_transactions_by_user_id(self, user_id: int):
        wallet = self.get_wallet_by_user_id(user_id)
        return wallet.transactions.all().order_by('-created_at')
