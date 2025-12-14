from typing import Dict, Any, List
from rest_framework.exceptions import ValidationError

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

    # ============ QUOTATION OPS ============ #
    def get_quotation_detail(self, user: User, quotation_id: int) -> Quotation:
        """ مشاهده جزئیات استعلام """
        # ===== بررسی مجوز مشاهده ===== #
        AppPermissionChecker.check_has_permission(user, 'view_quotation')
        
        quotation = self._quotation_repo.get_quotation_detail(quotation_id)
        if not quotation:
            raise ValidationError("استعلام مورد نظر یافت نشد.")
        return quotation

    # ============ CREATE QUOTATION ============ #
    def create_quotation(self, requester: User, data: Dict[str, Any]):
        """ 
        ایجاد یک استعلام قیمت جدید.
        """
        # ===== بررسی مجوز ایجاد ===== #
        AppPermissionChecker.check_has_permission(requester, 'add_quotation')
        # ===== دریافت مشتری ===== #
        customer_id = data.get('customer_id')
        customer = self._user_repo.get_by_id(customer_id)
        
        if not customer:
            raise ValidationError("مشتری با این شناسه یافت نشد.")
        
        is_valid_customer = customer.user_role.filter(role__is_customer=True).exists()
        if not is_valid_customer:
            raise ValidationError("این شخص مشتری نیست.")
        
        # ===== اجرای عملیات ===== #
        return self._domain_service.create_quotation(
            customer=customer,
            creator=requester, 
            data=data
        )
        
    # ============ UPDATE QUOTATION ============ #
    def update_quotation(self, requester: User, quotation_id: int, data: Dict[str, Any]):
        """ ویرایش پیش‌فاکتور """
        AppPermissionChecker.check_has_permission(requester, 'change_quotation')
        return self._domain_service.update_quotation(quotation_id, data)

    # ============ DELETE QUOTATION ============ #
    def delete_quotation(self, requester: User, quotation_id: int):
        """ حذف پیش‌فاکتور """
        AppPermissionChecker.check_has_permission(requester, 'delete_quotation')
        self._domain_service.delete_quotation(quotation_id)

    def update_quotation_status(self, user: User, quotation_id: int, status: str):
        """ 
        تغییر وضعیت استعلام (مثلاً: Sent, Accepted, Rejected).
        """
        # ===== بررسی مجوز تغییر ===== #
        AppPermissionChecker.check_has_permission(user, 'change_quotation')
        return self._domain_service.update_quotation_status(quotation_id, status, user)
    def convert_to_invoice(self, user: User, quotation_id: int, order_id: int):
        """ 
        تبدیل پیش‌فاکتور به فاکتور اصلی برای یک سفارش موجود.
        """
        # ===== بررسی مجوز (ادمین/فروش/مالی) ===== #
        AppPermissionChecker.check_has_permission(user, 'add_invoice') 
        
        return self._domain_service.convert_quotation_to_invoice(
            quotation_id=quotation_id, 
            user=user, 
            order_id=order_id
        )