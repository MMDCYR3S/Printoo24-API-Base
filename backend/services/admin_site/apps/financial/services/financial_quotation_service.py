from typing import Dict, Any

from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.db import transaction

from core.models import User, Quotation
from core.domain.identity.users import UserRepository
from core.domain.commerce.order import OrderRepository
from core.domain.financial import FinancialDomainService, QuotationRepository
from core.domain.infrastructure.logger.services import AuditLogDomainService
from apps.permissions import AppPermissionChecker

# ========== FINANCIAL QUOTATION SERVICE ========== #
class FinancialQuotationAppService:
    """
    سرویس اپلیکیشن مدیریت استعلام قیمت و پیش‌فاکتورهای رسمی.
    مسئولیت‌ها:
    - ایجاد استعلام جدید
    - تغییر وضعیت (ارسال به مشتری، تایید مشتری)
    - تبدیل به سفارش نهایی
    """
    
    def __init__(self):
        self._domain_service = FinancialDomainService()
        self._quotation_repo = QuotationRepository()
        self._user_repo = UserRepository()
        self._order_repo = OrderRepository()
        self.audit_service = AuditLogDomainService()

    # ============ READ ============ #
    def get_quotation_detail(self, user: User, quotation_id: int) -> Quotation:
        """
        دریافت جزییات یک استعلام
        """
        AppPermissionChecker.check_has_permission(user, 'view_quotation')
        quotation = self._quotation_repo.get_quotation_detail(quotation_id)
        if not quotation:
            raise ValidationError("استعلام یافت نشد.")
        return quotation

    # ============ CREATE QUOTATION ============ #
    @transaction.atomic
    def create_quotation(self, requester: User, order_id: int, data: Dict[str, Any]):
        """ 
        ایجاد استعلام: 
        1. ولیدیشن در App Service
        2. ایجاد در Repository
        3. محاسبه در Domain Service
        """
        AppPermissionChecker.check_has_permission(requester, 'add_quotation')
        # ===== ایجاد استعلام ===== #
        data = {**data, "converted_order": order_id}
        quotation = self._quotation_repo.create({**data, "created_by": requester})

        # ===== ثبت لاگ ===== #
        self.audit_service.record_log(
            user=requester,
            obj=quotation,
            action='CREATE_QUOTATION',
            changes={'order_id': order_id, 'initial_price': str(quotation.total_price)},
            description=_(f"ایجاد استعلام قیمت جدید")
        )

        return quotation
        
    # ============ UPDATE QUOTATION ============ #
    @transaction.atomic
    def update_quotation(self, requester: User, quotation_id: int, data: Dict[str, Any]):
        AppPermissionChecker.check_has_permission(requester, 'change_quotation')
        
        quotation = self._quotation_repo.get_by_id(quotation_id)
        if not quotation: raise ValidationError("استعلام یافت نشد.")
        
        if quotation.status == Quotation.Status.CONVERTED:
             raise ValidationError("استعلام تبدیل شده قابل ویرایش نیست.")
        # ===== بروزرسانی ===== #
        updated_quotation = self._quotation_repo.update(quotation, data)

        # ===== ثبت لاگ ===== #
        self.audit_service.record_log(
            user=requester,
            obj=updated_quotation,
            action='UPDATE_QUOTATION',
            changes={'updated_fields': list(data.keys())},
            description=_(f"ویرایش اطلاعات استعلام")
        )
        return updated_quotation

    # ============ DELETE QUOTATION ============ #
    def delete_quotation(self, requester: User, quotation_id: int):
        AppPermissionChecker.check_has_permission(requester, 'delete_quotation')
        quotation = self._quotation_repo.get_by_id(quotation_id)
        if not quotation: raise ValidationError("استعلام یافت نشد.")
        
        if quotation.status != Quotation.Status.DRAFT:
             raise ValidationError("فقط پیش‌نویس قابل حذف است.")
         
        quotation_number = quotation.quotation_number
        self._quotation_repo.delete(quotation)

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
        quotation = self._quotation_repo.get_by_id(quotation_id)
        
        if not quotation: raise ValidationError("استعلام یافت نشد.")

        old_status = quotation.status
        quotation.status = status
        quotation.save()
        
        # ===== ثبت لاگ ===== #
        self.audit_service.record_log(
            user=user,
            obj=quotation,
            action='QUOTATION_STATUS_CHANGE',
            changes={'from': old_status, 'to': status},
            description=_(f"تغییر وضعیت استعلام به {status}")
        )
        return quotation
    
    @transaction.atomic
    def convert_to_invoice(self, user: User, quotation_id: int, order_id: int):
        """ 
        منطق پیچیده تبدیل: کاملاً به Domain واگذار می‌شود.
        چون شامل ساخت فاکتور جدید، تغییر وضعیت استعلام و چک کردن سفارش است.
        """
        AppPermissionChecker.check_has_permission(user, 'add_invoice') 
        return self._domain_service.convert_quotation_to_invoice(quotation_id, user, order_id)
