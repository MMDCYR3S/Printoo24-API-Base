from rest_framework.exceptions import ValidationError, PermissionDenied
from typing import Dict, Any, List, Optional

from apps.permissions import AppPermissionChecker
from core.models import User, OrderCostReport, OrderCostItem, OrderCostCatalog
from core.domain.commerce.order import (
    OrderCostDomainService, OrderCostReportRepository,
    OrderCostItemRepository, OrderRepository
)
from core.domain.financial import FinancialDomainService


# ========== Financial App Service ========== #
class FinancialAppService:
    """
    سرویس اپلیکیشن برای مدیریت کامل فرآیندهای مالی (Cost Reports, Catalog, Approval).
    مسئولیت: چک دسترسی و هماهنگی بین ریپازیتوری‌ها و سرویس‌های دامنه مالی.
    """
    def __init__(self):
        # ===== تزریق وابستگی‌های دامنه ===== #
        self._cost_domain = OrderCostDomainService() 
        self._report_repo = OrderCostReportRepository()
        self._item_repo = OrderCostItemRepository()
        self._order_repo = OrderRepository()
        
    def get_report_details(self, user: User, report_id: int) -> OrderCostReport:
        """ مشاهده جزئیات یک گزارش هزینه """
        AppPermissionChecker.check_has_permission(user, 'view_cost_report')
        
        report = self._report_repo.model.objects.prefetch_related('items').filter(id=report_id).first()
        if not report:
            raise ValidationError("گزارش یافت نشد.")
        return report
    
    def create_manual_cost(self, user: User, order_id: int, data: Dict[str, Any]):
        """ ایجاد دستی هزینه توسط مدیر مالی """
        AppPermissionChecker.check_has_permission(user, 'add_cost_report')
        order = self._order_repo.get_by_id(order_id)
        
        if not order:
            raise ValidationError("سفارش یافت نشد.")
        
        return self._cost_domain.create_cost_report(
            order=order,
            user=user,
            title=data['title'],
            description=data.get('description', ''),
            attachment=data.get('attachment'),
            items_data=data['items']
        )
    
    def update_cost_report(self, user: User, report_id: int, data: Dict[str, Any]):
        """ ویرایش هدر گزارش """
        AppPermissionChecker.check_has_permission(user, 'change_cost_report')
        return self._cost_domain.update_cost_report_header(report_id, user, data)

    def delete_cost_report(self, user: User, report_id: int):
        """ حذف کامل گزارش """
        AppPermissionChecker.check_has_permission(user, 'delete_cost_report')
        self._cost_domain.delete_cost_report(report_id, user)

    def toggle_approval(self, user: User, report_id: int, approve: bool):
        """ تایید یا لغو تایید مالی """
        AppPermissionChecker.check_has_permission(user, 'approve_costs')
        return self._cost_domain.approve_cost_report(report_id, user, approve)
    
    # ========== مدیریت اقلام هزینه ========== #
    def add_item_to_report(self, user: User, report_id: int, data: Dict[str, Any]):
        """ اضافه کردن یک آیتم جدید به گزارش موجود """
        AppPermissionChecker.check_has_permission(user, 'change_cost_report')

        report = self._report_repo.get_by_id(report_id)
        if report.is_approved_by_finance:
            raise ValidationError("گزارش تایید شده است.")
            
        return self._cost_domain.item_repo.create({
            "report": report,
            "catalog_item_id": data.get('catalog_id'),
            "custom_title": data.get('custom_title'),
            "amount": data['amount'],
            "description": data.get('description')
        })

    def update_item(self, user: User, item_id: int, data: Dict[str, Any]):
        """ ویرایش یک آیتم """
        AppPermissionChecker.check_has_permission(user, 'change_cost_report')
        return self._cost_domain.update_cost_item(item_id, user, data)

    def delete_item(self, user: User, item_id: int):
        """ حذف یک آیتم """
        AppPermissionChecker.check_has_permission(user, 'change_cost_report')
        self._cost_domain.delete_cost_item(item_id, user)
        
    # ========== مدیریت فاکتورها و تراکنش‌ها ========== #
    def get_invoice_details(self, user: User, invoice_id: int):
        """ مشاهده جزئیات فاکتور """
        AppPermissionChecker.check_has_permission(user, 'financial.view_invoice')
        return FinancialDomainService().invoice_repo.get_invoice_detail(invoice_id)

    def recalculate_invoice_manually(self, user: User, invoice_id: int):
        """ دکمه 'محاسبه مجدد' برای مدیر مالی """
        AppPermissionChecker.check_has_permission(user, 'financial.change_invoice')
        
        domain = FinancialDomainService()
        invoice = domain.invoice_repo.get_by_id(invoice_id)
        if not invoice: raise ValidationError("فاکتور یافت نشد")
            
        return domain.recalculate_invoice(invoice)

    def finalize_invoice(self, user: User, invoice_id: int):
        """ تبدیل پیش فاکتور به فاکتور نهایی """
        AppPermissionChecker.check_has_permission(user, 'financial.change_invoice')
        return self.domain.confirm_invoice_final(invoice_id, user)

    def update_invoice(self, user: User, invoice_id: int, data: dict):
        """ ویرایش متادیتای فاکتور """
        AppPermissionChecker.check_has_permission(user, 'financial.change_invoice')
        return self.domain.update_invoice_metadata(invoice_id, data, user)

    def delete_invoice(self, user: User, invoice_id: int):
        """ حذف فاکتور """
        AppPermissionChecker.check_has_permission(user, 'financial.delete_invoice')
        self.domain.delete_invoice(invoice_id, user)
    
    # ========== مدیریت تراکنش‌ها ========== #
    def register_payment(self, user: User, invoice_id: int, data: dict):
        """ ثبت فیش دستی توسط ادمین مالی """
        AppPermissionChecker.check_has_permission(user, 'financial.add_transaction')
        return FinancialDomainService().register_manual_transaction(invoice_id, user, data)

    def verify_payment(self, user: User, transaction_id: int, approved: bool, reason: str = None):
        """ تایید یا رد تراکنش """
        AppPermissionChecker.check_has_permission(user, 'financial.change_transaction')
        return FinancialDomainService().verify_transaction(transaction_id, user, approved, reason)
    
    def update_transaction(self, user: User, transaction_id: int, data: dict):
        AppPermissionChecker.check_has_permission(user, 'financial.change_transaction')
        return self.domain.update_transaction_details(transaction_id, data, user)

    def delete_transaction(self, user: User, transaction_id: int):
        AppPermissionChecker.check_has_permission(user, 'financial.delete_transaction')
        self.domain.delete_transaction(transaction_id, user)
    