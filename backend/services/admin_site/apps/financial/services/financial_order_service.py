from typing import Dict, Any, List

from rest_framework.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.utils.translation import gettext_lazy as _
from django.db import transaction

from apps.permissions import AppPermissionChecker
from core.models import (
    User, OrderCostReport, OrderCostSheet,
    OrderCostCategory, OrderCostAttachment,
    OrderCostItem
)
from core.domain.commerce.order import (
    OrderCostDomainService, 
    OrderCostReportRepository, 
    OrderCostSheetRepository,
    OrderCostCategoryRepository,
    OrderCostAttachmentRepository,
    OrderCostItemRepository,
    OrderRepository,
    OrderCostDomainService 
)
from core.domain.infrastructure.logger.services import AuditLogDomainService

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
        # ===== سرویس دامنه ===== #
        self._domain_service = OrderCostDomainService()
        self.audit_service = AuditLogDomainService()
        # ===== ریپازیتوری ها ===== #
        self._report_repo = OrderCostReportRepository()
        self._sheet_repo = OrderCostSheetRepository()
        self._item_repo = OrderCostItemRepository()
        self._category_repo = OrderCostCategoryRepository()
        self._attachment_repo = OrderCostAttachmentRepository()
        self._order_repo = OrderRepository()
    
    # ============ CATEGORY MANAGEMENT ============ #
    def get_all_categories(self, user: User) -> List[OrderCostCategory]:
        AppPermissionChecker.check_has_permission(user, 'view_ordercostcategory')
        return self._category_repo.get_all_active()

    @transaction.atomic
    def create_category(self, user: User, data: Dict[str, Any]) -> OrderCostCategory:
        AppPermissionChecker.check_has_permission(user, 'add_ordercostcategory')
        
        if self._category_repo.get_by_slug(data.get('slug')):
            raise ValidationError("کد دسته‌بندی (slug) تکراری است.")
            
        category = self._category_repo.create(data)

        # ===== ثبت لاگ ===== #
        self.audit_service.record_log(
            user=user,
            obj=category,
            action='CREATE_COST_CATEGORY',
            changes={'title': category.title, 'slug': category.slug},
            description=_(f"ایجاد دسته‌بندی هزینه: {category.title}")
        )
        return category

    @transaction.atomic
    def update_category(self, user: User, category_id: int, data: Dict[str, Any]) -> OrderCostCategory:
        AppPermissionChecker.check_has_permission(user, 'change_ordercostcategory')
        
        category = self._category_repo.get_by_id(category_id)
        if not category:
            raise ValidationError("دسته‌بندی یافت نشد.")

        # ===== چک کردن اینکه آیا کد تکراری است ===== #
        new_slug = data.get('slug')
        if new_slug and new_slug != category.slug:
            if self._category_repo.get_by_slug(new_slug):
                raise ValidationError("کد دسته‌بندی تکراری است.")

        updated_cat = self._category_repo.update(category, data)

        # ===== ثبت لاگ ===== #
        self.audit_service.record_log(
            user=user,
            obj=updated_cat,
            action='UPDATE_COST_CATEGORY',
            changes={'updated_fields': list(data.keys())},
            description=_(f"ویرایش دسته‌بندی هزینه: {updated_cat.name}")
        )
        return updated_cat
    @transaction.atomic
    def delete_category(self, user: User, category_id: int) -> None:
        AppPermissionChecker.check_has_permission(user, 'delete_ordercostcategory')
        
        category = self._category_repo.get_by_id(category_id)
        if not category:
            raise ValidationError("دسته‌بندی یافت نشد.")
            
        # ===== چک کردن اینکه آیا دسته بندی زیرمجموعه داره یا نه ===== #
        if self._item_repo.filter(catalog_item_id=category_id).exists():
             raise ValidationError("این دسته‌بندی در گزارش‌های مالی استفاده شده و قابل حذف نیست.")
             
        cat_name = category.title
        self._category_repo.delete(category)

        # ===== ثبت لاگ حذف ===== #
        self.audit_service.record_log(
            user=user,
            obj=None,
            action='DELETE_COST_CATEGORY',
            changes={'deleted_id': category_id, 'title': cat_name},
            description=_(f"حذف دسته‌بندی هزینه")
        )
    
    # ============ REPORT MANAGEMENT ============ #
    @transaction.atomic
    def create_report_manually(self, user: User, order_id: int, data: Dict, items: List[Dict], attachments: List[UploadedFile] = []) -> OrderCostReport:
        """
        ایجاد کامل گزارش هزینه شامل هدر، آیتم‌ها و پیوست‌ها.
        """
        AppPermissionChecker.check_has_permission(user, 'add_ordercostreport')
        # ===== گزارش شیت ===== #
        sheet = self._ensure_sheet_exists(order_id)
        # ===== بررسی قفل نبودن سند مالی ===== #
        self._domain_service._validate_sheet_is_modifiable(sheet)
        # ===== ایجاد هدر گزارش ===== #
        report_data = {
            "sheet": sheet,
            "submitter": user,
            "department": data.get("department", "finance"),
            "title": data["title"],
            "description": data.get("description", ""),
            "is_approved": False
        }
        report = self._report_repo.create(report_data)
        
        # ===== ایجاد آیتم‌ها و پیوست‌ها ===== #
        self._bulk_create_items(report, items)
        if attachments:
            self._create_attachments(report, attachments)
        
        # ===== محاسبه مجدد ===== #
        self._domain_service.recalculate_sheet_totals(sheet)
        
        # ===== ثبت لاگ جامع ===== #
        self.audit_service.record_log(
            user=user,
            obj=report.sheet,
            action='CREATE_COST_REPORT',
            changes={
                'report_id': report.id,
                'title': report.title,
                'items_count': len(items),
                'total_amount': sum(float(i.get('amount', 0)) for i in items)
            },
            description=_(f"ثبت گزارش هزینه جدید: {report.title}")
        )
        
        return report
    
    # ============ REPORT CRUD (Financial Edit) ============ #
    @transaction.atomic
    def update_report(self, user: User, report_id: int, data: Dict) -> OrderCostReport:
        AppPermissionChecker.check_has_permission(user, 'change_ordercostreport')
        # ===== بررسی قانون قفل نبودن سند مالی ===== #
        report = self._domain_service.validate_report_modification(report_id)
        # ===== تغییرات اصلی ===== #
        updated_report = self._report_repo.update(report, data)
        self._domain_service.recalculate_sheet_totals(updated_report.sheet)

        # ===== ثبت لاگ ===== #
        self.audit_service.record_log(
            user=user,
            obj=updated_report.sheet,
            action='UPDATE_COST_REPORT',
            changes={'report_id': report_id, 'updated_fields': list(data.keys())},
            description=_(f"ویرایش هدر گزارش هزینه: {updated_report.title}")
        )

        return updated_report

    @transaction.atomic
    def delete_report(self, user: User, report_id: int) -> None:
        AppPermissionChecker.check_has_permission(user, 'delete_ordercostreport')
        # ===== اعتبارسنجی گزارش مالی ===== #
        report = self._domain_service.validate_report_modification(report_id)
        sheet = report.sheet
        report_title = report.title
        total_value = report.total_amount

        self._report_repo.delete(report)
        self._domain_service.recalculate_sheet_totals(sheet)

        # ===== ثبت لاگ حذف ===== #
        self.audit_service.record_log(
            user=user,
            obj=sheet,
            action='DELETE_COST_REPORT',
            changes={'deleted_report_id': report_id, 'title': report_title, 'value_removed': str(total_value)},
            description=_(f"حذف گزارش هزینه")
        )

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

    def approve_report(self, user: User, report_id: int) -> OrderCostReport:
        """ تایید یا رد گزارش هزینه """
        AppPermissionChecker.check_has_permission(user, 'approve_ordercostreport')
        return self._domain_service.approve_report(report_id, user)

    def reject_report(self, user: User, report_id: int) -> OrderCostReport:
        """ رد گزارش هزینه """
        AppPermissionChecker.check_has_permission(user, 'approve_ordercostreport')
        return self._domain_service.reject_report(report_id, user)

    # ============ ITEM CRUD (Financial Edit) ============ #
    @transaction.atomic
    def add_item_to_report(self, user: User, report_id: int, data: Dict) -> OrderCostItem:
        AppPermissionChecker.check_has_permission(user, 'change_ordercostreport')

        report = self._report_repo.get_by_id(report_id)
        if not report: raise ValidationError("گزارش یافت نشد.")

        # ===== اعتبارسنجی گزارش ===== #
        self._domain_service.validate_item_modification(report)
        # ===== آماده سازی ===== #
        if 'category_id' in data:
            data['catalog_item'] = self._category_repo.get_by_id(data.pop('category_id'))
        data['report'] = report
        # ===== ایجاد ===== #
        item = self._item_repo.create(data)
        self._domain_service.recalculate_sheet_totals(report.sheet)

        # ===== ثبت لاگ آیتم ===== #
        self.audit_service.record_log(
            user=user,
            obj=report.sheet,
            action='ADD_COST_ITEM',
            changes={'report_id': report_id, 'amount': str(item.amount), 'description': item.description},
            description=_(f"افزودن آیتم هزینه جدید")
        )
        return item

    @transaction.atomic
    def update_report_item(self, user: User, item_id: int, data: Dict) -> OrderCostItem:
        AppPermissionChecker.check_has_permission(user, 'change_ordercostreport')

        item = self._item_repo.get_by_id(item_id)
        if not item: raise ValidationError("آیتم یافت نشد.")
        self._domain_service.validate_item_modification(item.report)
        if 'category_id' in data:
            data['catalog_item'] = self._category_repo.get_by_id(data.pop('category_id'))
        # ===== آپدیت ===== #
        old_amount = item.amount
        updated_item = self._item_repo.update(item, data)
        self._domain_service.recalculate_sheet_totals(item.report.sheet)

        # ===== ثبت لاگ ===== #
        self.audit_service.record_log(
            user=user,
            obj=item.report.sheet,
            action='UPDATE_COST_ITEM',
            changes={
                'item_id': item_id, 
                'amount_change': f"{old_amount} -> {updated_item.amount}",
                'updated_fields': list(data.keys())
            },
            description=_(f"ویرایش آیتم هزینه")
        )
        return updated_item

    @transaction.atomic
    def delete_report_item(self, user: User, item_id: int) -> None:
        AppPermissionChecker.check_has_permission(user, 'change_ordercostreport')

        item = self._item_repo.get_by_id(item_id)
        if not item: raise ValidationError("آیتم یافت نشد.")
        # ===== اعتبارسنجی ===== #
        self._domain_service.validate_item_modification(item.report)
        sheet = item.report.sheet
        deleted_amount = str(item.amount)
        # ===== حذف ===== #
        self._item_repo.delete(item)
        # ===== محاسبه مجدد ===== #
        self._domain_service.recalculate_sheet_totals(sheet)
        
        # ===== ثبت لاگ حذف ===== #
        self.audit_service.record_log(
            user=user,
            obj=sheet,
            action='DELETE_COST_ITEM',
            changes={'deleted_item_id': item_id, 'amount_removed': deleted_amount},
            description=_(f"حذف آیتم هزینه")
        )

    # ============ SHEET MANAGEMENT ============ #
    @transaction.atomic
    def create_sheet(self, user: User, order_id: int) -> OrderCostSheet:
        """
        ایجاد دستی سند مالی (Ledger) برای یک سفارش.
        """
        AppPermissionChecker.check_has_permission(user, 'add_ordercostsheet')
        # ===== بررسی تکراری نبودن ===== #
        if self._sheet_repo.get_by_order_id(order_id):
            raise ValidationError("سند مالی برای این سفارش قبلاً ایجاد شده است.")
        # ===== بررسی وجود سفارش ===== #
        if not self._order_repo.filter(id=order_id).exists():
             raise ValidationError("سفارش مورد نظر یافت نشد.")
        # ===== ایجاد ===== #
        sheet = self._sheet_repo.create({"order_id": order_id})

        # ===== ثبت لاگ ===== #
        self.audit_service.record_log(
            user=user,
            obj=sheet,
            action='CREATE_COST_SHEET',
            description=_(f"افتتاح سند مالی سفارش")
        )
        return sheet

    @transaction.atomic
    def update_sheet(self, user: User, sheet_id: int, data: Dict[str, Any]) -> OrderCostSheet:
        """
        ویرایش اطلاعات کلی سند مالی.
        """
        AppPermissionChecker.check_has_permission(user, 'change_ordercostsheet')
        # ===== بازیابی سند ===== #
        sheet = self._sheet_repo.get_by_id(sheet_id)
        if not sheet:
            raise ValidationError("سند مالی یافت نشد.")
        # ===== ویرایش ===== #
        updated_sheet = self._sheet_repo.update(sheet, data)
        # ===== محاسبه مجدد ===== #
        self._domain_service.recalculate_sheet_totals(updated_sheet)
        
        return updated_sheet

    @transaction.atomic
    def delete_sheet(self, user: User, sheet_id: int) -> None:
        """
        حذف سند مالی.
        قانون بیزنس: سندی که دارای گزارش تایید شده (گردش مالی) باشد، نباید حذف شود.
        """
        AppPermissionChecker.check_has_permission(user, 'delete_ordercostsheet')
        # ===== بازگیری سند ===== #
        sheet = self._sheet_repo.get_by_id(sheet_id)
        if not sheet:
            raise ValidationError("سند مالی یافت نشد.")
        # ===== بررسی تکراری ===== #
        has_approved_reports = self._report_repo.filter(sheet=sheet, is_approved=True).exists()
        if has_approved_reports:
             raise ValidationError("این سند دارای گزارش‌های تایید شده است و قابل حذف نیست. ابتدا گزارش‌ها را رد/حذف کنید.")
        # ===== حذف ===== #
        order_code = sheet.order.order_code if sheet.order else "Unknown"
        self._sheet_repo.delete(sheet)
        # ===== ثبت لاگ حذف ===== #
        self.audit_service.record_log(
            user=user,
            obj=None,
            action='DELETE_COST_SHEET',
            changes={'deleted_sheet_id': sheet_id, 'order_code': order_code},
            description=_(f"حذف سند مالی سفارش")
        )
    
    def get_order_cost_sheet(self, user: User, order_id: int) -> OrderCostSheet:
        """ 
        مشاهده سند کل بهای تمام شده سفارش.
        """
        AppPermissionChecker.check_has_permission(user, 'view_ordercostsheet')
        
        sheet = self._sheet_repo.get_by_order_id(order_id)
        if not sheet:
            raise ValidationError("سند مالی برای این سفارش هنوز ایجاد نشده است.")
            
        return sheet

    # ========== FINANCIAL SUMMARY ========== #
    def get_financial_summary(self, user: User, order_id: int) -> Dict[str, Any]:
        """
        دریافت خلاصه مدیریتی (Dashboard View).
        مناسب برای نمایش اعداد کلیدی بدون بارگذاری کل آبجکت‌ها.
        """
        # ===== بررسی مجوز مشاهده ===== #
        AppPermissionChecker.check_has_permission(user, 'view_ordercostsheet')
        return self._domain_service.get_order_financial_summary(order_id)

    # ========== LOCK ORDER COSTS ========== #
    def lock_order_costs(self, user: User, order_id: int) -> OrderCostSheet:
        """
        قفل کردن حساب سفارش
        """
        AppPermissionChecker.check_has_permission(user, 'lock_ordercostsheet')
        return self._domain_service.lock_cost_sheet(order_id, user)

    # ========== INTERNAL METHODS ========== #
    def _ensure_sheet_exists(self, order_id: int) -> OrderCostSheet:
        sheet = self._sheet_repo.get_by_order_id(order_id)
        if not sheet:
            if not self._order_repo.filter(id=order_id).exists():
                raise ValidationError("سفارش یافت نشد.")
            sheet = self._sheet_repo.create({"order_id": order_id})
        return sheet

    def _bulk_create_items(self, report: OrderCostReport, items_data: List[Dict]):
        """Helper to create multiple items at once"""
        new_items = []
        for item_data in items_data:
            category = None
            if item_data.get('category_id'):
                category = self._category_repo.get_by_id(item_data['category_id'])
            
            new_items.append(OrderCostItem(
                report=report,
                catalog_item=category,
                custom_title=item_data.get('custom_title'),
                amount=item_data.get('amount', 0),
                description=item_data.get('description', '')
            ))
        
        if new_items:
            self._item_repo.bulk_create_items(new_items)

    def _create_attachments(self, report: OrderCostReport, files: List[UploadedFile]):
        """Helper to create attachments"""
        attachments = []
        for file in files:
            attachments.append(
                self._attachment_repo.model(report=report, file=file, title=file.name)
            )
        self._attachment_repo.bulk_create_attachments(attachments)
