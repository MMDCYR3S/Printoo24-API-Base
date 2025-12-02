from decimal import Decimal
from django.db.models import QuerySet
from core.models import Wallet, User
from core.domain.wallet import WalletDomainService
from core.domain.users import UserRepository
from rest_framework.exceptions import NotFound, ValidationError

class WalletDashboardService:
    """
    سرویس مدیریت کیف پول مخصوص داشبورد ادمین.
    این سرویس از لاجیک‌های هسته (DomainService) استفاده می‌کند.
    """
    def __init__(self):
        self.domain_service = WalletDomainService()
        self.user_repo = UserRepository()

    # ===== دریافت لیست کیف پول‌ها ===== #
    def get_wallets_queryset(self) -> QuerySet[Wallet]:
        """
        لیست کیف پول‌ها را با بهینه‌سازی (select_related) برمی‌گرداند.
        """
        return Wallet.objects.select_related('user__customer_profile').all().order_by('-updated_at')

    # ===== عملیات اصلاح موجودی (Adjustment) ===== #
    def adjust_balance(self, user_id: int, amount: Decimal, action_type: str) -> Wallet:
        """
        مدیریت افزایش یا کاهش موجودی توسط ادمین.
        action_type: 'deposit' | 'withdraw'
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFound("کاربر مورد نظر یافت نشد.")

        if amount <= 0:
            raise ValidationError("مبلغ باید بزرگتر از صفر باشد.")

        # ارجاع به سرویس دامین برای تضمین تراکنش اتمیک
        if action_type == 'deposit':
            return self.domain_service.deposit(user, amount)
        elif action_type == 'withdraw':
            return self.domain_service.debit(user, amount)
        else:
            raise ValidationError("نوع عملیات نامعتبر است.")