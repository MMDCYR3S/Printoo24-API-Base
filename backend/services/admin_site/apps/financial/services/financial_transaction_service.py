from typing import Dict, Any, List

from django.db import transaction
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from core.models import User, Invoice
from apps.financial.domain_services import TransactionService
from apps.support.services import LoggerService
from apps.financial.models import Transaction
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
        self._domain_service = TransactionService()
        self.audit_service = LoggerService()

    # ============ LIST TRANSACTIONS ============ #
    def list_transactions(self, user: User, filters: Dict[str, Any] = None) -> List[Transaction]:
        AppPermissionChecker.check_has_permission(user, 'view_transaction')
        queryset = Transaction.objects.all().select_related('invoice', 'user').order_by('-created_at')
        if filters:
            if 'status' in filters:
                queryset = queryset.filter(status=filters['status'])
            if 'invoice_id' in filters:
                queryset = queryset.filter(invoice_id=filters['invoice_id'])
                
        return queryset

    # ============ GET TRANSACTION DETAIL ============ #
    def get_transaction_detail(self, user: User, transaction_id: int) -> Transaction:
        AppPermissionChecker.check_has_permission(user, 'view_transaction')
        trx = Transaction.objects.get_by_id(transaction_id)
        if not trx: 
            raise ValidationError("تراکنش یافت نشد.")
        return trx

    # ============= REGISTER PAYMENT ============ #
    def register_manual_payment(self, user: User, invoice_id: int, data: Dict[str, Any]):
        """ 
        ثبت فیش دستی: فقط ایجاد رکورد (CRUD). 
        هنوز اثر مالی ندارد (Pending است)، پس نیازی به Domain Service نیست.
        """
        AppPermissionChecker.check_has_permission(user, 'add_transaction')
        # ===== بررسی وجود فاکتور ===== #
        try:
            invoice = Invoice.objects.get(id=invoice_id)
        except Invoice.DoesNotExist:
            raise ValidationError("فاکتور یافت نشد.")
        
        # ===== ایجاد رکورد ===== #
        allowed_fields = ['amount', 'method', 'receipt_image', 'tracking_code', 'payment_date', 'dest_account']
        clean_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        trx = Transaction.objects.create(
            **clean_data,
            invoice=invoice,
            user=user,
            status='pending'
        )

        # ===== ثبت لاگ ===== #
        self.audit_service.record_log(
            user=user,
            obj=trx,
            action='REGISTER_PAYMENT',
            changes={'amount': str(trx.amount), 'invoice_id': invoice.id, 'method': trx.method},
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
        # ===== بررسی وجود ===== #
        trx = Transaction.objects.get_by_id(transaction_id)
        if not trx: raise ValidationError("تراکنش یافت نشد.")
        # ===== بررسی وضعیت و در صورت اتمام، عدم دسترسی به تغییر ===== #
        if trx.status != 'pending':
            raise ValidationError("تراکنش‌های تعیین تکلیف شده قابل ویرایش نیستند.")
        # ====== آماده سازی فایل ها برای ایجاد رکورد ===== #
        allowed_fields = ['amount', 'method', 'tracking_code', 'payment_date', 'dest_account']
        for key in allowed_fields:
            if key in data:
                setattr(trx, key, data[key])
        # ====== در صورت وجود عکس ===== #
        if 'receipt_image' in data:
            trx.receipt_image = data['receipt_image']
            
        trx.save()
        
        # ===== ثبت لاگ ===== #
        self.audit_service.record_log(
            user=user,
            obj=trx,
            action='UPDATE_TRANSACTION',
            changes={'updated_fields': list(data.keys())},
            description=_(f"ویرایش جزئیات تراکنش")
        )
            
        return trx
    
    # ============ DELETE TRANSACTION ============ #
    def delete_transaction(self, user: User, transaction_id: int):
        AppPermissionChecker.check_has_permission(user, 'delete_transaction')
        
        trx = Transaction.objects.get_by_id(transaction_id)
        if not trx: raise ValidationError("تراکنش یافت نشد.")
        
        if trx.status != 'pending':
             raise ValidationError("نمی‌توان تراکنش تایید/رد شده را حذف کرد.")
             
        amount = str(trx.amount)
        trx_id = trx.id

        trx.delete()

        # ===== ثبت لاگ حذف ===== #
        self.audit_service.record_log(
            user=user,
            obj=None,
            action='DELETE_TRANSACTION',
            changes={'deleted_id': trx_id, 'amount': amount},
            description=_(f"حذف تراکنش معلق")
        )
