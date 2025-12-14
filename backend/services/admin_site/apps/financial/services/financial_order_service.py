from rest_framework.exceptions import ValidationError
from typing import Dict, Any, List

from apps.permissions import AppPermissionChecker
from core.models import User, OrderCostReport, OrderCostSheet
from core.domain.commerce.order import (
    OrderCostDomainService, 
    OrderCostReportRepository, 
    OrderCostSheetRepository,
    OrderRepository
)

# ============ Financial Order App Service ============ #
class FinancialOrderAppService:
    """
    سرویس اپلیکیشن مدیریت هزینه‌های سفارش (Cost Accounting).
    
    وظایف اصلی:
    1. مدیریت گزارش‌های واصله از واحدها (مشاهده، تایید، رد)
    2. نظارت بر بهای تمام شده (مشاهده شیت و سود/زیان)
    3. عملیات پایان دوره سفارش (قفل کردن حساب‌ها)
    """
    
    def __init__(self):
        self._domain_service = OrderCostDomainService()
        self._report_repo = OrderCostReportRepository()
        self._sheet_repo = OrderCostSheetRepository()
        self._order_repo = OrderRepository()
    
    # ============ REPORT MANAGEMENT ============ #
    def get_order_reports(self, user: User, order_id: int) -> List[OrderCostReport]:
        """ 
        مشاهده لیست تمام گزارش‌های هزینه یک سفارش خاص.
        """
        # ===== بررسی مجوز مشاهده ===== #
        AppPermissionChecker.check_has_permission(user, 'view_ordercostreport')
        
        sheet = self._sheet_repo.get_by_order_id(order_id)
        if not sheet:
            return []
            
        return self._report_repo.get_reports_by_sheet(sheet.id)

    def get_report_detail(self, user: User, report_id: int) -> OrderCostReport:
        """ 
        مشاهده جزئیات یک گزارش هزینه خاص به همراه اقلام و پیوست‌ها.
        """
        # ===== بررسی مجوز مشاهده ===== #
        AppPermissionChecker.check_has_permission(user, 'view_ordercostreport')
        
        report = self._report_repo.get_report_detail(report_id)
        if not report:
            raise ValidationError("گزارش هزینه مورد نظر یافت نشد.")
        return report

    def approve_report(self, user: User, report_id: int):
        """ 
        تایید نهایی گزارش هزینه توسط مدیر مالی.
        نکته: این عملیات باعث محاسبه مجدد شیت مادر می‌شود.
        """
        # ===== بررسی مجوز تغییر (تایید) ===== #
        AppPermissionChecker.check_has_permission(user, 'change_ordercostreport')
        
        return self._domain_service.approve_report(report_id, user)

    def reject_report(self, user: User, report_id: int, reason: str):
        """ 
        رد کردن گزارش هزینه (عودت به واحد مربوطه جهت اصلاح).
        """
        # ===== بررسی مجوز تغییر (رد) ===== #
        AppPermissionChecker.check_has_permission(user, 'change_ordercostreport')
        
        if not reason:
            raise ValidationError("ذکر دلیل رد برای گزارش الزامی است.")
            
        return self._domain_service.reject_report(report_id, user, reason)

    # ============ SHEET MANAGEMENT ============ #
    def get_order_cost_sheet(self, user: User, order_id: int) -> OrderCostSheet:
        """ 
        مشاهده سند کل بهای تمام شده سفارش (Ledger).
        شامل سود، زیان، حاشیه سود و وضعیت قفل بودن.
        """
        # ===== بررسی مجوز مشاهده ===== #
        AppPermissionChecker.check_has_permission(user, 'view_ordercostsheet')
        
        sheet = self._sheet_repo.get_by_order_id(order_id)
        if not sheet:
            raise ValidationError("سند مالی برای این سفارش هنوز ایجاد نشده است.")
            
        return sheet

    def get_financial_summary(self, user: User, order_id: int) -> Dict[str, Any]:
        """
        دریافت خلاصه مدیریتی (Dashboard View).
        مناسب برای نمایش اعداد کلیدی بدون بارگذاری کل آبجکت‌ها.
        """
        # ===== بررسی مجوز مشاهده ===== #
        AppPermissionChecker.check_has_permission(user, 'view_ordercostsheet')
        
        return self._domain_service.get_order_financial_summary(order_id)

    def lock_order_costs(self, user: User, order_id: int):
        """ 
        بستن نهایی حساب‌های سفارش (Locking).
        پس از این کار، هیچ هزینه‌ای قابل ثبت یا تغییر نیست.
        معمولاً پس از تحویل سفارش و تسویه نهایی انجام می‌شود.
        """
        # ===== بررسی مجوز قفل کردن ===== #
        AppPermissionChecker.check_has_permission(user, 'change_ordercostsheet')
        
        return self._domain_service.lock_cost_sheet(order_id, user)
