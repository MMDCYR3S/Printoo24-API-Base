from typing import Dict, Any
from rest_framework.exceptions import ValidationError

from core.models import User, Invoice
from core.domain.financial import FinancialDomainService, InvoiceRepository
from core.domain.commerce.order import OrderRepository
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
        self._domain_service = FinancialDomainService()
        self._invoice_repo = InvoiceRepository()
        self._order_repo = OrderRepository()

    # ========================================== #
    # ============ READ OPERATIONS ============= #
    # ========================================== #
    def get_invoice_detail(self, user: User, invoice_id: int) -> Invoice:
        """ مشاهده جزئیات کامل فاکتور و لاگ‌ها """
        # ===== بررسی مجوز مشاهده ===== #
        AppPermissionChecker.check_has_permission(user, 'view_invoice')
        
        invoice = self._invoice_repo.get_invoice_detail(invoice_id)
        if not invoice:
            raise ValidationError("فاکتور مورد نظر یافت نشد.")
        return invoice

    # ========================================== #
    # ============ WRITE OPERATIONS ============ #
    # ========================================== #
    def create_invoice_manually(self, user: User, order_id: int):
        """ 
        ایجاد دستی فاکتور برای سفارشی که فاقد فاکتور است.
        """
        # ===== بررسی مجوز ایجاد ===== #
        AppPermissionChecker.check_has_permission(user, 'add_invoice')
        
        order = self._order_repo.get_by_id(order_id)
        if not order:
            raise ValidationError("سفارش یافت نشد.")
            
        return self._domain_service.force_create_invoice(order, user)

    def recalculate_invoice(self, user: User, invoice_id: int):
        """ 
        محاسبه مجدد مبالغ فاکتور (آپدیت مالیات و خدمات).
        """
        # ===== بررسی مجوز تغییر ===== #
        AppPermissionChecker.check_has_permission(user, 'change_invoice')
        return self._domain_service.recalculate_invoice(invoice_id)

    def finalize_invoice(self, user: User, invoice_id: int):
        """ 
        تبدیل پیش‌فاکتور به فاکتور نهایی (قطعی کردن فروش).
        """
        # ===== بررسی مجوز تغییر ===== #
        AppPermissionChecker.check_has_permission(user, 'change_invoice')
        return self._domain_service.confirm_invoice_final(invoice_id, user)

    def update_invoice_metadata(self, user: User, invoice_id: int, data: Dict[str, Any]):
        """ 
        ویرایش اطلاعات غیر مالی فاکتور (توضیحات، سررسید).
        """
        # ===== بررسی مجوز تغییر ===== #
        AppPermissionChecker.check_has_permission(user, 'change_invoice')
        return self._domain_service.update_invoice_metadata(invoice_id, data, user)

    def delete_invoice(self, user: User, invoice_id: int):
        """ 
        حذف فاکتور (فقط در شرایط مجاز).
        """
        # ===== بررسی مجوز حذف ===== #
        AppPermissionChecker.check_has_permission(user, 'delete_invoice')
        self._domain_service.delete_invoice(invoice_id, user)
