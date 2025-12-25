from typing import Dict, Any

from django.db import transaction
from django.utils.translation import gettext as _
from rest_framework.exceptions import ValidationError

from core.models import User, Invoice, Order
from apps.financial.domain_services import FinancialService
from apps.support.services import LoggerService
from apps.permissions import AppPermissionChecker

class FinancialInvoiceAppService:
    """
    سرویس اپلیکیشن اختصاصی مدیریت فاکتورها.
    مسئولیت‌ها:
    - مشاهده جزئیات
    - صدور دستی/سیستمی
    - اصلاح و بروزرسانی مبالغ
    - نهایی‌سازی و حذف
    """
    
    def __init__(self):
        self._domain_service = FinancialService()
        self.audit_service = LoggerService()

    # ============ READ ============ #
    def get_invoice_detail(self, user: User, invoice_id: int) -> Invoice:
        AppPermissionChecker.check_has_permission(user, 'view_invoice')
        invoice = Invoice.objects.get_invoice_detail(invoice_id)
        if not invoice:
            raise ValidationError("فاکتور مورد نظر یافت نشد.")
        return invoice

    # ============ WRITE ============ #
    @transaction.atomic
    def create_invoice_manually(self, user: User, order_id: int):
        """ ایجاد فاکتور: چون شامل منطق بیزنس (کپی آیتم‌ها از سفارش) است، به دامین می‌سپاریم. """
        AppPermissionChecker.check_has_permission(user, 'add_invoice')
        
        order = Order.objects.get_order_by_id(order_id)
        if not order:
            raise ValidationError("سفارش یافت نشد.")
            
        return self._domain_service.issue_invoice_from_order(order, user)

    @transaction.atomic
    def update_invoice(self, user: User, invoice_id: int, data: Dict[str, Any]):
        """ 
        ویرایش فاکتور: 
        1. آپدیت داده‌های خام توسط منیجر/ORM
        2. درخواست محاسبه مجدد از دامین
        """
        AppPermissionChecker.check_has_permission(user, 'change_invoice')
        # ===== دریافت و بررسی وجود فاکتور ===== #
        try:
            invoice = Invoice.objects.get(id=invoice_id)
        except Invoice.DoesNotExist:
            raise ValidationError("فاکتور یافت نشد.")
        
        # ===== چک کردن ===== #
        if invoice.status in [Invoice.Status.FINALIZE, Invoice.Status.PAID_FULL]:
             raise ValidationError("امکان ویرایش فاکتور نهایی شده وجود ندارد.")

        # ===== آپدیت دستی ===== #
        for key, value in data.items():
            if hasattr(invoice, key):
                setattr(invoice, key, value)
        invoice.save()
        
        # ===== ثبت لاگ ویرایش دستی ===== #
        self.audit_service.record_log(
            user=user,
            obj=invoice,
            action='UPDATE_INVOICE_DATA',
            changes={'updated_fields': list(data.keys())},
            description=_(f"ویرایش دستی اقلام فاکتور")
        )

        # ===== انجام محاسبات ===== #
        return self._domain_service.recalculate_invoice_totals(invoice, user)

    @transaction.atomic
    def finalize_invoice(self, user: User, invoice_id: int):
        """ عملیات حساس تغییر وضعیت به نهایی """
        AppPermissionChecker.check_has_permission(user, 'change_invoice')
        # ===== بررسی وجود فاکتور ===== #
        try:
            invoice = Invoice.objects.get(id=invoice_id)
        except Invoice.DoesNotExist:
            raise ValidationError("فاکتور یافت نشد.")
        
        return self._domain_service.confirm_invoice_final(invoice, user)

    @transaction.atomic
    def delete_invoice(self, user: User, invoice_id: int):
        """ حذف فاکتور: مستقیم با ریپازیتوری (با چک کردن گاردها) """
        AppPermissionChecker.check_has_permission(user, 'delete_invoice')
        
        try:
            invoice = Invoice.objects.get(id=invoice_id)
        except Invoice.DoesNotExist:
            raise ValidationError("فاکتور یافت نشد.")
        
        if invoice.status != Invoice.Status.PENDING:
            raise ValidationError("تنها پیش‌نویس فاکتور قابل حذف است.")
        
        inv_number = invoice.invoice_number

        invoice.delete()
        
        # ===== ثبت لاگ حذف ===== #
        self.audit_service.record_log(
            user=user,
            obj=None,
            action='DELETE_INVOICE',
            changes={'deleted_id': invoice_id, 'invoice_number': inv_number},
            description=_(f"حذف پیش‌نویس فاکتور")
        )
