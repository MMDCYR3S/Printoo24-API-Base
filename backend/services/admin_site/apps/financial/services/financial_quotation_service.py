from typing import Dict, Any

from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.db import transaction

from core.models import Order, User, Quotation
from core.financial.services import FinancialService
from core.logger.services import LoggerService
from apps.permissions import AppPermissionChecker

# ========== FINANCIAL QUOTATION SERVICE ========== #
class FinancialQuotationAppService:
    """
    سرویس اپلیکیشن مدیریت پیش‌فاکتور قیمت و پیش‌فاکتورهای رسمی.
    مسئولیت‌ها:
    - ایجاد پیش‌فاکتور جدید
    - تغییر وضعیت (ارسال به مشتری، تایید مشتری)
    - تبدیل به سفارش نهایی
    """
    
    def __init__(self):
        self._domain_service = FinancialService()
        self.audit_service = LoggerService()

    # ============ READ ============ #
    def get_quotation_detail(self, user: User, quotation_id: int) -> Quotation:
        """
        دریافت جزییات یک پیش‌فاکتور
        """
        AppPermissionChecker.check_has_permission(user, 'view_quotation')
        quotation = Quotation.objects.get_quotation_detail(quotation_id)
        if not quotation:
            raise ValidationError("پیش‌فاکتور یافت نشد.")
        return quotation

    # ============ CREATE QUOTATION ============ #
    @transaction.atomic
    def create_quotation(self, requester: User, order_id: int, data: Dict[str, Any]):
        """ 
        ایجاد پیش‌فاکتور جدید.
        """
        AppPermissionChecker.check_has_permission(requester, 'add_quotation')
        # ===== بررسی وجود سفارش مرتبط ===== #
        if not Order.objects.filter(pk=order_id).exists():
            raise ValidationError("سفارش مرتبط یافت نشد.")

        # ===== آماده سازی داده ها ===== #
        create_data = {
            **data, 
            "converted_order_id": order_id,
            "created_by": requester
        }
        # ===== ایجاد پیش فاکتور ===== #
        quotation = Quotation.objects.create(**create_data)

        # ===== ثبت لاگ ===== #
        self.audit_service.record_log(
            user=requester,
            obj=quotation,
            action='CREATE_QUOTATION',
            changes={'order_id': order_id, 'initial_price': str(quotation.total_price)},
            description=_(f"ایجاد پیش‌فاکتور قیمت جدید")
        )

        return quotation
        
    # ============ UPDATE QUOTATION ============ #
    # ============ UPDATE QUOTATION ============ #
    @transaction.atomic
    def update_quotation(self, requester: User, quotation_id: int, data: Dict[str, Any]):
        AppPermissionChecker.check_has_permission(requester, 'change_quotation')
        # ===== بررسی وجود پیش فاکتور ===== #
        try:
            quotation = Quotation.objects.get(id=quotation_id)
        except Quotation.DoesNotExist:
            raise ValidationError("پیش‌فاکتور یافت نشد.")
        
        if quotation.status == Quotation.Status.CONVERTED:
             raise ValidationError("پیش‌فاکتور تبدیل شده قابل ویرایش نیست.")
        
        # ===== بروزرسانی فیلدهای مربوط به پیش فاکتور ===== #
        for key, value in data.items():
            if hasattr(quotation, key):
                setattr(quotation, key, value)
        quotation.save()

        # ===== ثبت لاگ ویرایش ===== #
        self.audit_service.record_log(
            user=requester,
            obj=quotation,
            action='UPDATE_QUOTATION',
            changes={'updated_fields': list(data.keys())},
            description=_(f"ویرایش اطلاعات پیش‌فاکتور")
        )
        return quotation

    # ============ DELETE QUOTATION ============ #
    def delete_quotation(self, requester: User, quotation_id: int):
        AppPermissionChecker.check_has_permission(requester, 'delete_quotation')
        # ===== بررسی وجود پیش‌فاکتور ===== #
        try:
            quotation = Quotation.objects.get(id=quotation_id)
        except Quotation.DoesNotExist:
            raise ValidationError("پیش فاکتور یافت نشد.")
        
        if quotation.status != Quotation.Status.DRAFT:
             raise ValidationError("فقط پیش‌نویس قابل حذف است.")
         
        quotation_number = quotation.quotation_number
        quotation.delete()

        # ===== ثبت لاگ حذف ===== #
        self.audit_service.record_log(
            user=requester,
            obj=None,
            action='DELETE_QUOTATION',
            changes={'deleted_id': quotation_id, 'quotation_number': quotation_number},
            description=_(f"حذف پیش‌نویس استعلام")
        )
        
    def update_quotation_status(self, user: User, quotation_id: int, status: str):
        """ تغییر وضعیت ساده (بدون محاسبه) """
        AppPermissionChecker.check_has_permission(user, 'change_quotation')
        # ===== بررسی وجود پیش‌فاکتور ===== #
        try:
            quotation = Quotation.objects.get(id=quotation_id)
        except Quotation.DoesNotExist:
            raise ValidationError("پیش فاکتور یافت نشد.")
        # ===== تغییر وضعیت ===== #
        old_status = quotation.status
        quotation.status = status
        quotation.save()
        
        # ===== ثبت لاگ ===== #
        self.audit_service.record_log(
            user=user,
            obj=quotation,
            action='QUOTATION_STATUS_CHANGE',
            changes={'from': old_status, 'to': status},
            description=_(f"تغییر وضعیت پیش‌فاکتور به {status}")
        )
        return quotation
    
    @transaction.atomic
    def convert_to_invoice(self, user: User, quotation_id: int, order_id: int):
        """ 
        منطق پیچیده تبدیل: کاملاً به Domain واگذار می‌شود.
        چون شامل ساخت فاکتور جدید، تغییر وضعیت پیش‌فاکتور و چک کردن سفارش است.
        """
        AppPermissionChecker.check_has_permission(user, 'add_invoice') 
        return self._domain_service.convert_quotation_to_invoice(quotation_id, user, order_id)
