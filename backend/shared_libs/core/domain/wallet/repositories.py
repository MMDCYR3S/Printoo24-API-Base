from typing import List, Optional, Any

from django.core.exceptions import ObjectDoesNotExist

from .exceptions import (
    WalletNotFoundException
)
from ...utils.base_repository import BaseRepository
from core.models import User, Wallet, WalletTransaction

# ======== Wallet Repository ======== #
class WalletRepository(BaseRepository[Wallet]):
    """
    مخزن انتزاعی برای کیف پول مشتری
    """
    def __init__(self):
        super().__init__(Wallet)

    # ===== دریافت کیف پول یک کاربر ===== #
    def get_by_user(self, user: User) -> Optional[Wallet]:
        """
        دریافت کیف پول یک کاربر
        """
        try:
            return self.model.objects.get(user=user)
        except ObjectDoesNotExist:
            raise WalletNotFoundException("کیف پول برای این کاربر یافت نشد.")
        
    # ===== دریافت کیف پول با قفل کردن رکورد ===== #
    def get_for_update(self, user_id: int) -> Wallet:
        """
        دریافت کیف پول با قفل کردن رکورد دیتابیس
        برای جلوگیری از Race Condition هنگام واریز/برداشت
        """
        try:
            return self.model.objects.select_for_update().get(user_id=user_id)
        except self.model.DoesNotExist:
            return self.model.objects.create(user_id=user_id)
        
    def get_locked_wallet(self, user: User) -> Wallet:
        """
        دریافت کیف پول با قفل ردیف (Row Lock).
        باید حتماً داخل transaction.atomic صدا زده شود.
        اگر کیف پول نباشد، می‌سازد (Safe Create).
        """
        wallet, _ = self.model.objects.select_for_update().get_or_create(
            user=user,
            defaults={'decimal': 0}
        )
        return wallet
        
# ======== Wallet Transaction Repository ======== #
class WalletTransactionRepository(BaseRepository[WalletTransaction]):
    """
    مخزن انتزاعی برای تراکنش های کیف پول

    """
    def __init__(self):
        super().__init__(WalletTransaction)
        
    def create_transaction(self, user: User, trans_type: str, amount: float, amount_after: float) -> WalletTransaction:
        return self.create({
            "user": user,
            "type": trans_type,
            "amount": amount,
            "amount_after": amount_after
        })

    def get_history_by_user(self, user_id: int) -> List[WalletTransaction]:
        """دریافت تاریخچه تراکنش‌ها به ترتیب نزولی"""
        return self.model.objects.filter(user_id=user_id).order_by('-created_at')
