from typing import Dict, Any, List
from django.db import transaction
from rest_framework.exceptions import ValidationError

from core.models import User, Transaction
from core.domain.financial import FinancialDomainService, TransactionRepository
from apps.permissions import AppPermissionChecker

# ========== Financial Transaction App Service ========== #
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

    # ============ LIST TRANSACTIONS ============ #
    def list_transactions(self, user: User, filters: Dict[str, Any] = None) -> List[Transaction]:
        AppPermissionChecker.check_has_permission(user, 'view_transaction')
        return self._trx_repo.filter_transactions(filters).order_by('-created_at')

    # ============ GET TRANSACTION DETAIL ============ #
    def get_transaction_detail(self, user: User, transaction_id: int) -> Transaction:
        AppPermissionChecker.check_has_permission(user, 'view_transaction')
        trx = self._trx_repo.get_by_id(transaction_id)
        if not trx: raise ValidationError("تراکنش یافت نشد.")
        return trx

    # ============= REGISTER PAYMENT ============ #
    def register_manual_payment(self, user: User, invoice_id: int, data: Dict[str, Any]):
        """ 
        ثبت فیش: فقط ایجاد رکورد (CRUD). 
        هنوز اثر مالی ندارد (Pending است)، پس نیازی به Domain Service نیست.
        """
        AppPermissionChecker.check_has_permission(user, 'add_transaction')
        
        invoice = self._invoice_repo.get_by_id(invoice_id)
        if not invoice: raise ValidationError("فاکتور یافت نشد.")
        
        # ===== ایجاد رکورد ===== #
        trx_data = {
            **data,
            "invoice": invoice,
            "created_by": user,
            "status": "pending"
        }
        return self._trx_repo.create(trx_data)

    # ============ VERIFY TRANSACTION ============ #
    @transaction.atomic
    def verify_transaction(self, user: User, transaction_id: int, approved: bool, reason: str = None):
        """ 
        تایید/رد: این یک قانون بیزنس است چون روی مانده حساب فاکتور اثر می‌گذارد.
        پس به Domain Service واگذار می‌شود.
        """
        AppPermissionChecker.check_has_permission(user, 'change_transaction')
        
        if not approved and not reason:
            raise ValidationError("ذکر دلیل رد تراکنش الزامی است.")
            
        return self._domain_service.verify_transaction(transaction_id, user, approved, reason)

    # ============ UPDATE TRANSACTION ============ #
    def update_transaction(self, user: User, transaction_id: int, data: Dict[str, Any]):
        """ ویرایش جزئیات تراکنش (فقط در صورتی که پندینگ باشد) """
        AppPermissionChecker.check_has_permission(user, 'change_transaction')
        
        trx = self._trx_repo.get_by_id(transaction_id)
        if not trx: raise ValidationError("تراکنش یافت نشد.")
        
        if trx.status != 'pending':
            raise ValidationError("تراکنش‌های تعیین تکلیف شده قابل ویرایش نیستند.")
            
        return self._trx_repo.update(trx, data)
    
    # ============ DELETE TRANSACTION ============ #
    def delete_transaction(self, user: User, transaction_id: int):
        AppPermissionChecker.check_has_permission(user, 'delete_transaction')
        
        trx = self._trx_repo.get_by_id(transaction_id)
        if not trx: raise ValidationError("تراکنش یافت نشد.")
        
        if trx.status != 'pending':
             raise ValidationError("نمی‌توان تراکنش تایید/رد شده را حذف کرد.")
             
        self._trx_repo.delete(trx)
