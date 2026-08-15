from decimal import Decimal

from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from .exceptions import WalletNotFoundException

from core.infrastructure.messages import msg_provider

# ===== Base QuerySet ===== #
class BaseQuerySet(models.QuerySet):
    """
    متدهای پایه برای شبیه‌سازی رفتار Repository
    """
    
    def get_by_id(self, id: int):
        """
        دریافت رکورد با ID.
        اگر پیدا نشد، None برمی‌گرداند (برای حفظ منطق سرویس‌های قبلی)
        """
        return self.filter(id=id).first()

# ========== Wallet QuerySet ========== #
class WalletQuerySet(BaseQuerySet):
    """
    کوئری‌های مربوط به کیف پول
    """
    def get_by_user(self, user):
        """
        دریافت کیف پول یک کاربر.
        طبق منطق قبلی، اگر نباشد خطا برمی‌گرداند.
        """
        try:
            return self.get(user=user)
        except ObjectDoesNotExist:
            raise WalletNotFoundException(msg_provider.get("wallet.E3003"))

    def get_for_update_custom(self, user_id: int):
        """
        دریافت کیف پول با قفل کردن رکورد دیتابیس (متد قدیمی Repo)
        """
        try:
            return self.select_for_update().get(user_id=user_id)
        except ObjectDoesNotExist:
            return self.create(user_id=user_id)

    def get_locked_wallet(self, user):
        """
        دریافت کیف پول با قفل ردیف (Row Lock).
        باید حتماً داخل transaction.atomic صدا زده شود.
        اگر کیف پول نباشد، می‌سازد (Safe Create).
        """
        wallet, _ = self.select_for_update().get_or_create(
            user=user,
            defaults={'balance': 0}
        )
        return wallet

# ========== Wallet Manager ========== #
class WalletManager(models.Manager):
    def get_queryset(self):
        return WalletQuerySet(self.model, using=self._db)

    def get_by_user(self, user):
        return self.get_queryset().get_by_user(user)

    def get_for_update(self, user_id: int):
        return self.get_queryset().get_for_update_custom(user_id)

    def get_locked_wallet(self, user):
        return self.get_queryset().get_locked_wallet(user)


# ========== Wallet Transaction Manager ========== #
class WalletTransactionManager(models.Manager):
    """
    مدیر تراکنش‌های کیف پول با امضای جدید
    """

    def create_transaction(
        self,
        wallet,
        user,
        transaction_type,
        amount,
        balance_before,
        balance_after,
        description="",
        created_by=None,
        order=None,
        payment=None,
        invoice=None,
    ):
        """
        ایجاد تراکنش با تمام جزئیات لازم
        """
        return self.create(
            wallet=wallet,
            user=user,
            transaction_type=transaction_type,
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            description=description,
            created_by=created_by,
            order=order,
            payment=payment,
            invoice=invoice,
        )

    def get_history_by_user(self, user_id: int):
        """
        دریافت تاریخچه تراکنش‌های یک کاربر به ترتیب نزولی
        """
        return self.filter(user_id=user_id).order_by('-created_at')
