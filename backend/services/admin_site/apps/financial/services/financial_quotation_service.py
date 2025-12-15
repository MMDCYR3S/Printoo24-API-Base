from typing import Dict, Any, List
from rest_framework.exceptions import ValidationError
from django.db import transaction

from core.models import User, Quotation
from core.domain.identity.users import UserRepository
from core.domain.financial import FinancialDomainService, QuotationRepository
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
    def create_quotation(self, requester: User, data: Dict[str, Any]):
        """ 
        ایجاد استعلام: 
        1. ولیدیشن در App Service
        2. ایجاد در Repository
        3. محاسبه در Domain Service
        """
        AppPermissionChecker.check_has_permission(requester, 'add_quotation')
        
        # ===== بررسی مشتری ===== #
        customer_id = data.get('user')
        customer = self._user_repo.get_by_id(customer_id)
        if not customer:
            raise ValidationError("مشتری یافت نشد.")
        
        data = {**data, "user": customer}
        # ===== ایجاد استعلام ===== #
        quotation = self._quotation_repo.create({**data, "created_by": requester})
        
        # ===== محاسبه ===== #
        return self._domain_service.recalculate_quotation_totals(quotation)
        
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
        
        # ===== محاسبه ===== #
        return self._domain_service.recalculate_quotation_totals(updated_quotation)

    # ============ DELETE QUOTATION ============ #
    def delete_quotation(self, requester: User, quotation_id: int):
        AppPermissionChecker.check_has_permission(requester, 'delete_quotation')
        quotation = self._quotation_repo.get_by_id(quotation_id)
        if not quotation: raise ValidationError("استعلام یافت نشد.")
        
        if quotation.status != Quotation.Status.DRAFT:
             raise ValidationError("فقط پیش‌نویس قابل حذف است.")
             
        self._quotation_repo.delete(quotation)

    
    def update_quotation_status(self, user: User, quotation_id: int, status: str):
        """ تغییر وضعیت ساده (بدون محاسبه) """
        AppPermissionChecker.check_has_permission(user, 'change_quotation')
        quotation = self._quotation_repo.get_by_id(quotation_id)
        
        if not quotation: raise ValidationError("استعلام یافت نشد.")

        quotation.status = status
        quotation.save()
        return quotation
    
    @transaction.atomic
    def convert_to_invoice(self, user: User, quotation_id: int, order_id: int):
        """ 
        منطق پیچیده تبدیل: کاملاً به Domain واگذار می‌شود.
        چون شامل ساخت فاکتور جدید، تغییر وضعیت استعلام و چک کردن سفارش است.
        """
        AppPermissionChecker.check_has_permission(user, 'add_invoice') 
        return self._domain_service.convert_quotation_to_invoice(quotation_id, user, order_id)
