from typing import Dict, Any, List
from rest_framework.exceptions import ValidationError

from core.models import User, Quotation
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

    # ============ QUOTATION OPS ============ #
    def get_quotation_detail(self, user: User, quotation_id: int) -> Quotation:
        """ مشاهده جزئیات استعلام """
        # ===== بررسی مجوز مشاهده ===== #
        AppPermissionChecker.check_has_permission(user, 'view_quotation')
        
        quotation = self._quotation_repo.get_quotation_detail(quotation_id)
        if not quotation:
            raise ValidationError("استعلام مورد نظر یافت نشد.")
        return quotation

    def create_quotation(self, user: User, data: Dict[str, Any], items: List[Dict[str, Any]]):
        """ 
        ایجاد یک استعلام قیمت جدید.
        """
        # ===== بررسی مجوز ایجاد ===== #
        AppPermissionChecker.check_has_permission(user, 'add_quotation')
        return self._domain_service.create_quotation(user, data, items)

    def update_quotation_status(self, user: User, quotation_id: int, status: str):
        """ 
        تغییر وضعیت استعلام (مثلاً: Sent, Accepted, Rejected).
        """
        # ===== بررسی مجوز تغییر ===== #
        AppPermissionChecker.check_has_permission(user, 'change_quotation')
        return self._domain_service.update_quotation_status(quotation_id, status, user)

    def convert_to_order(self, user: User, quotation_id: int, address_id: int):
        """ 
        تبدیل استعلام تایید شده به سفارش و صدور فاکتور.
        """
        # ===== بررسی مجوز تبدیل (معمولاً فروش یا مالی) ===== #
        AppPermissionChecker.check_has_permission(user, 'add_order') 
        
        return self._domain_service.convert_quotation_to_order(quotation_id, user, address_id)
