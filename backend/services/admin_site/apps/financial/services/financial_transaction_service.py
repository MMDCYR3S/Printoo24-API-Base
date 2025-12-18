from typing import Dict, Any, List

from django.db import transaction
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from core.models import User, Transaction
from core.domain.financial import FinancialDomainService, TransactionRepository
from core.domain.infrastructure.logger.services import AuditLogDomainService
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
        self.audit_service = AuditLogDomainService()

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
        trx = self._trx_repo.create(trx_data)

        # ===== ثبت لاگ ===== #
        self.audit_service.record_log(
            user=user,
            obj=trx,
            action='REGISTER_PAYMENT',
            changes={'amount': str(trx.amount), 'invoice_id': invoice.id, 'method': trx.payment_method},
            description=_(f"ثبت دستی فیش واریزی")
        )
        return trx

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
        
        updated_trx = self._trx_repo.update(trx, data)
        
        # ===== ثبت لاگ ===== #
        self.audit_service.record_log(
            user=user,
            obj=updated_trx,
            action='UPDATE_TRANSACTION',
            changes={'updated_fields': list(data.keys())},
            description=_(f"ویرایش جزئیات تراکنش")
        )
            
        return updated_trx
    
    # ============ DELETE TRANSACTION ============ #
    def delete_transaction(self, user: User, transaction_id: int):
        AppPermissionChecker.check_has_permission(user, 'delete_transaction')
        
        trx = self._trx_repo.get_by_id(transaction_id)
        if not trx: raise ValidationError("تراکنش یافت نشد.")
        
        if trx.status != 'pending':
             raise ValidationError("نمی‌توان تراکنش تایید/رد شده را حذف کرد.")
             
        amount = str(trx.amount)
        trx_id = trx.id

        self._trx_repo.delete(trx)

        # ===== ثبت لاگ حذف ===== #
        self.audit_service.record_log(
            user=user,
            obj=None,
            action='DELETE_TRANSACTION',
            changes={'deleted_id': trx_id, 'amount': amount},
            description=_(f"حذف تراکنش معلق")
        )
