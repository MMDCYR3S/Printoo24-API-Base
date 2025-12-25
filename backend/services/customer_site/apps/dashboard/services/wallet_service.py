import logging
from decimal import Decimal
from django.db.models import QuerySet
from django.db import transaction
from rest_framework.exceptions import NotFound, ValidationError

from apps.accounts.models import Wallet
from apps.accounts.domain_services import WalletService
from core.users.services import CustomerService


# ===== Logger ===== #
logger = logging.getLogger('dashboard.services.wallet')

class WalletDashboardService:
    """
    سرویس مدیریت کیف پول مخصوص داشبورد ادمین.
    """
    def __init__(self):
        self.domain_service = WalletService()
        self.user_repo = CustomerService()

    # ===== دریافت لیست کیف پول‌ها ===== #
    def get_wallets_queryset(self) -> QuerySet[Wallet]:
        """
        لیست کیف پول‌ها را با بهینه‌سازی (select_related) برمی‌گرداند.
        """
        # اینجا لاگ نمیگذاریم چون یک کوئری ساده خواندنی است
        return Wallet.objects.select_related('user__customer_profile').all().order_by('-updated_at')

    # ===== عملیات اصلاح موجودی (Adjustment) ===== #
    @transaction.atomic
    def adjust_balance(self, user_id: int, amount: Decimal, action_type: str) -> Wallet:
        """
        مدیریت افزایش یا کاهش موجودی توسط ادمین.
        action_type: 'deposit' | 'debit'
        """
        logger.info(f"START: Adjust balance for User {user_id}. Amount: {amount}, Type: {action_type}")
        
        try:
            user = self.user_repo.get_customer_by_id(user_id)
            if not user:
                raise NotFound("کاربر مورد نظر یافت نشد.")

            if amount <= 0:
                raise ValidationError("مبلغ باید بزرگتر از صفر باشد.")

            # ارجاع به سرویس دامین
            if action_type == 'deposit':
                wallet = self.domain_service.deposit(user, amount)
                logger.info(f"DEPOSIT SUCCESS: User {user_id}, New Balance: {wallet.decimal}")
                
            elif action_type == 'debit':
                wallet = self.domain_service.debit(user, amount)
                logger.info(f"DEBIT SUCCESS: User {user_id}, New Balance: {wallet.decimal}")
                
            else:
                raise ValidationError("نوع عملیات نامعتبر است.")
            
            return wallet

        except Exception as e:
            logger.error(f"FAILED: Adjust balance for User {user_id}. Error: {str(e)}", exc_info=True)
            raise e
