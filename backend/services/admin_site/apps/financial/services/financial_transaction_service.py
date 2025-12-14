from typing import Dict, Any
from rest_framework.exceptions import ValidationError

from core.models import User, Transaction
from core.domain.financial import FinancialDomainService, TransactionRepository
from apps.permissions import AppPermissionChecker

class FinancialTransactionAppService:
    """
    سرویس اپلیکیشن اختصاصی مدیریت تراکنش‌های مالی.
    مسئولیت‌ها:
    - ثبت دستی فیش
    - تایید/رد واریزی‌ها
    - ویرایش و حذف تراکنش‌های معلق
    """
    
    def __init__(self):
        self._domain_service = FinancialDomainService()
        self._trx_repo = TransactionRepository()

    # ============ TRANSACTION OPS ============ #
    def register_manual_payment(self, user: User, invoice_id: int, data: Dict[str, Any]):
        """ 
        ثبت دستی پرداخت (فیش بانکی/کارت‌به‌کارت) توسط ادمین مالی.
        """
        # ===== بررسی مجوز ثبت ===== #
        AppPermissionChecker.check_has_permission(user, 'add_transaction')
        return self._domain_service.register_manual_transaction(invoice_id, user, data)

    def verify_transaction(self, user: User, transaction_id: int, approved: bool, reason: str = None):
        """ 
        تایید یا رد تراکنش‌های در انتظار بررسی.
        """
        # ===== بررسی مجوز تایید ===== #
        AppPermissionChecker.check_has_permission(user, 'change_transaction')
        
        if not approved and not reason:
            raise ValidationError("ذکر دلیل رد تراکنش الزامی است.")
            
        return self._domain_service.verify_transaction(transaction_id, user, approved, reason)

    def update_transaction(self, user: User, transaction_id: int, data: Dict[str, Any]):
        """ 
        ویرایش جزئیات تراکنش (فقط تراکنش‌های Pending).
        """
        # ===== بررسی مجوز تغییر ===== #
        AppPermissionChecker.check_has_permission(user, 'change_transaction')
        return self._domain_service.update_transaction_details(transaction_id, data, user)

    def delete_transaction(self, user: User, transaction_id: int):
        """ 
        حذف تراکنش (فقط تراکنش‌های Pending).
        """
        # ===== بررسی مجوز حذف ===== #
        AppPermissionChecker.check_has_permission(user, 'delete_transaction')
        self._domain_service.delete_transaction(transaction_id, user)
