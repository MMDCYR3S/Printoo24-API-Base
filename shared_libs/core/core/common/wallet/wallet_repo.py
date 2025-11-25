from typing import List, Optional, Any

from django.core.exceptions import ObjectDoesNotExist

from ..repositories import IRepository
from core.models import User, Wallet, WalletTransaction

# ======== Wallet Repository ======== #
class WalletRepository(IRepository[Wallet]):
    """
    مخزن انتزاعی برای کیف پول مشتری
    """
    def __init__(self):
        super().__init__(Wallet)

    def get_by_user(self, user: User) -> Optional[Wallet]:
        """
        دریافت کیف پول یک کاربر
        """
        try:
            return self.model.objects.get(user=user)
        except ObjectDoesNotExist:
            return None
        
    
    def get_for_update(self, user_id: int) -> Wallet:
        """
        دریافت کیف پول با قفل کردن رکورد دیتابیس
        برای جلوگیری از Race Condition هنگام واریز/برداشت
        """
        try:
            return self.model.objects.select_for_update().get(user_id=user_id)
        except self.model.DoesNotExist:
            return self.model.objects.create(user_id=user_id)
        
# ======== Wallet Transaction Repository ======== #
class WalletTransactionRepository(IRepository[WalletTransaction]):
    """
    مخزن انتزاعی برای تراکنش های کیف پول

    """
    def __init__(self):
        super().__init__(WalletTransaction)
        
    def create_transaction(self, user: User, trans_type: str, amount: float, amount_after: float) -> WalletTransaction:
        data = {
            "user": user,
            "type": trans_type,
            "amount": amount,
            "amount_after": amount_after
        }
        return self.create(data)

    def get_history_by_user(self, user_id: int) -> List[WalletTransaction]:
        """دریافت تاریخچه تراکنش‌ها به ترتیب نزولی"""
        return self.model.objects.filter(user_id=user_id).order_by('-created_at')
