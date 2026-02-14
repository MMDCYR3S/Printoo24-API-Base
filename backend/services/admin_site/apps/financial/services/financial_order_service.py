from typing import Dict, Any, List

from rest_framework.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.utils.translation import gettext_lazy as _
from django.db import transaction

from core.models import User, Order
from apps.support.services import LoggerService
from apps.permissions import AppPermissionChecker
from apps.order.models import (
    OrderFinancialReport, OrderFinancialSheet, OrderFinancialCategory, 
    OrderFinancialItem, OrderFinancialAttachment, OrderFinancialType
)
from apps.order.domain_services import OrderFinancialService

# ============ FINANCIAL ORDER APP SERVICE ============ #
class FinancialOrderAppService:
    """
    سرویس اپلیکیشن مدیریت هزینه‌های سفارش (Financial Accounting).
    
    وظایف اصلی:
    1. مدیریت گزارش‌های واصله از واحدها (مشاهده، تایید، رد)
    2. نظارت بر بهای تمام شده (مشاهده شیت و سود/زیان)
    3. عملیات پایان دوره سفارش (قفل کردن حساب‌ها)
    """
    
    def __init__(self):
        self._domain_service = OrderFinancialService()
        self.audit_service = LoggerService()
    
    # ============ CATEGORY LIST ============ #
    def get_all_categories(self, user: User) -> List[OrderFinancialCategory]:
        AppPermissionChecker.check_has_permission(user, 'view_ordercostcategory')
        return OrderFinancialCategory.objects.get_all_active()

    # ============ CATEGORY CREATE ============ #
    @transaction.atomic
    def create_category(self, user: User, data: Dict[str, Any]) -> OrderFinancialCategory:
        AppPermissionChecker.check_has_permission(user, 'add_ordercostcategory')
        
        if OrderFinancialCategory.objects.get_by_slug(data.get('slug')):
            raise ValidationError("کد دسته‌بندی (slug) تکراری است.")
        # ===== ایجاد دسته‌بندی ===== #
        category = OrderFinancialCategory.objects.create(**data)

        # ===== ثبت لاگ ===== #
        self.audit_service.record_log(
            user=user,
            obj=category,
            action='CREATE_COST_CATEGORY',
            changes={'title': category.title, 'slug': category.slug},
            description=_(f"ایجاد دسته‌بندی هزینه: {category.title}")
        )
        return category

    # ============ CATEGORY UPDATE ============ #
    @transaction.atomic
    def update_category(self, user: User, category_id: int, data: Dict[str, Any]) -> OrderFinancialCategory:
        AppPermissionChecker.check_has_permission(user, 'change_ordercostcategory')
        # ===== بررسی وجود دسته بندی ===== #
        category = OrderFinancialCategory.objects.get_by_id(category_id)
        if not category:
            raise ValidationError("دسته‌بندی یافت نشد.")

        # ===== چک کردن اینکه آیا کد تکراری است ===== #
        new_slug = data.get('slug')
        if new_slug and new_slug != category.slug:
            if OrderFinancialCategory.objects.get_by_slug(new_slug):
                raise ValidationError("کد دسته‌بندی تکراری است.")
        # ===== بروزرسانی آیتم های مربوط به دسته بندی ===== #
        for key, value in data.items():
            setattr(category, key, value)
        category.save()

        # ===== ثبت لاگ ===== #
        self.audit_service.record_log(
            user=user,
            obj=category,
            action='UPDATE_COST_CATEGORY',
            changes={'updated_fields': list(data.keys())},
            description=_(f"ویرایش دسته‌بندی هزینه: {category.title}")
        )
        return category
    
    # ========== CATEGORY DELETE ============ #
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
    
    # ============ REPORT CREATE ============ #
    @transaction.atomic
    def create_report_manually(self, user: User, order_id: int, data: Dict, items: List[Dict] = [], attachments: List[UploadedFile] = []) -> OrderFinancialReport:
        """
        ایجاد کامل گزارش هزینه شامل هدر، آیتم‌ها و پیوست‌ها.
        """
        AppPermissionChecker.check_has_permission(user, 'add_ordercostreport')
        # ===== گزارش شیت ===== #
        sheet = self._ensure_sheet_exists(order_id)
        # ===== بررسی قفل نبودن سند مالی ===== #
        financial_tag = None
        self._domain_service._validate_sheet_is_modifiable(sheet)
        if data.get("financial_tag"):
            financial_tag = OrderFinancialType.objects.get(id=data.get("financial_tag"))
        else:
            pass
        # ===== ایجاد هدر گزارش ===== #
        report = OrderFinancialReport.objects.create(
            sheet=sheet,
            submitter=user,
            financial_tag=financial_tag if financial_tag else None,
            title=data["title"],
            description=data.get("description", ""),
            is_approved=False
        )
        
        # ===== ایجاد آیتم‌ها و پیوست‌ها ===== #
        if items:
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
                'items_count': len(items) if items else None
            },
            description=_(f"ثبت گزارش هزینه جدید: {report.title}")
        )
        return report
    
    # ============ REPORT UPDATE ============ #
    @transaction.atomic
    def update_report(self, user: User, order_id: int, report_id: int, data: Dict) -> OrderFinancialReport:
        AppPermissionChecker.check_has_permission(user, 'change_ordercostreport')
        # ===== بررسی قانون قفل نبودن سند مالی ===== #
        report = OrderFinancialReport.objects.get_by_order_and_id(order_id, report_id)
        if not report:
            raise ValidationError("گزارش مورد نظر در این سفارش یافت نشد.")
        # ===== تغییرات اصلی ===== #
        self._domain_service.validate_report_modification(report.id)
        
        for key, value in data.items():
            setattr(report, key, value)
        report.save()
        self._domain_service.recalculate_sheet_totals(report.sheet)

        self.audit_service.record_log(
            user=user,
            obj=report.sheet,
            action='UPDATE_COST_REPORT',
            changes={'report_id': report_id, 'order_id': order_id, 'updated_fields': list(data.keys())},
            description=_(f"ویرایش هدر گزارش هزینه: {report.title}")
        )
        return report

    # ============ REPORT DELETE ============ #
    @transaction.atomic
    def delete_report(self, user: User, order_id: int, report_id: int) -> None:
        AppPermissionChecker.check_has_permission(user, 'delete_ordercostreport')
        
        report = OrderFinancialReport.objects.get_by_order_and_id(order_id, report_id)
        if not report:
            raise ValidationError("گزارش مورد نظر در این سفارش یافت نشد.")
        
        self._domain_service.validate_report_modification(report.id)
        
        sheet = report.sheet
        report_title = report.title
        
        report.delete()
        self._domain_service.recalculate_sheet_totals(sheet)
        
        self.audit_service.record_log(
            user=user,
            obj=sheet,
            action='DELETE_COST_REPORT',
            changes={'deleted_report_id': report_id, 'order_id': order_id, 'title': report_title},
            description=_(f"حذف گزارش هزینه")
        )
    
    def get_all_reports(self, user: User, nature: str = None):
        """ نمایش تمامی گزارشات (هزینه یا درآمد) """
        queryset = OrderFinancialReport.objects.get_all()
        if nature:
            queryset = queryset.filter(nature=nature)
        return queryset

    # ============ REPORT LIST ============ #
    def get_order_reports(self, user: User, order_id: int) -> List[OrderFinancialReport]:
        """ 
        مشاهده لیست تمام گزارش‌های هزینه یک سفارش خاص.
        """
        # ===== بررسی مجوز مشاهده ===== #
        AppPermissionChecker.check_has_permission(user, 'view_ordercostreport')
        
        sheet = OrderFinancialSheet.objects.get_by_order_id(order_id)
        if not sheet:
            return []
            
        return OrderFinancialReport.objects.get_reports_by_sheet(sheet.id)

    # ============ REPORT DETAIL ============ #
    def get_report_detail(self, user: User, order_id: int, report_id: int) -> OrderFinancialReport:
        """ 
        مشاهده جزئیات یک گزارش هزینه خاص به همراه اقلام و پیوست‌ها.
        """
        # ===== بررسی مجوز مشاهده ===== #
        AppPermissionChecker.check_has_permission(user, 'view_ordercostreport')
        report = OrderFinancialReport.objects.get_by_order_and_id(order_id, report_id)
        if not report:
            raise ValidationError("گزارش مورد نظر در این سفارش یافت نشد.")
        return report
    
    # ============ REPORT APPROVE ============ #
    def approve_report(self, user: User, report_id: int) -> OrderFinancialReport:
        """ تایید یا رد گزارش هزینه """
        AppPermissionChecker.check_has_permission(user, 'approve_ordercostreport')
        return self._domain_service.approve_report(report_id, user)

    def reject_report(self, user: User, report_id: int) -> OrderFinancialReport:
        """ رد گزارش هزینه """
        AppPermissionChecker.check_has_permission(user, 'approve_ordercostreport')
        return self._domain_service.reject_report(report_id, user)

    # ============ ITEM CRUD (Financial Edit) ============ #
    @transaction.atomic
    def add_item_to_report(self, user: User, report_id: int, data: Dict) -> OrderFinancialItem:
        AppPermissionChecker.check_has_permission(user, 'change_ordercostreport')

        report = OrderFinancialReport.objects.get_by_id(report_id)
        if not report: raise ValidationError("گزارش یافت نشد.")

        # ===== اعتبارسنجی گزارش ===== #
        self._domain_service.validate_item_modification(report)
        # ===== آماده سازی ===== #
        if 'category_id' in data:
            data['catalog_item'] = OrderFinancialCategory.objects.get_by_id(data.pop('category_id'))
        # ===== ایجاد آیتم ===== #
        item = OrderFinancialItem.objects.create(report=report, **data)
        self._domain_service.recalculate_sheet_totals(report.sheet)
        # ===== ثبت لاگ ===== #
        self.audit_service.record_log(
            user=user,
            obj=report.sheet,
            action='ADD_COST_ITEM',
            changes={'report_id': report_id, 'amount': str(item.amount)},
            description=_(f"افزودن آیتم هزینه جدید")
        )
        return item

    # =========== ITEM UPDATE ============ # 
    @transaction.atomic
    def update_report_item(self, user: User, item_id: int, data: Dict) -> OrderFinancialItem:
        AppPermissionChecker.check_has_permission(user, 'change_ordercostreport')

        item = OrderFinancialItem.objects.get_by_id(item_id)
        if not item: raise ValidationError("آیتم یافت نشد.")
        self._domain_service.validate_item_modification(item.report)
        if 'category_id' in data:
            data['catalog_item'] = OrderFinancialCategory.objects.get_by_id(data.pop('category_id'))
        # ===== آپدیت ===== #
        old_amount = item.amount
        for key, value in data.items():
            setattr(item, key, value)
        item.save()
        self._domain_service.recalculate_sheet_totals(item.report.sheet)

        # ===== ثبت لاگ ===== #
        self.audit_service.record_log(
            user=user,
            obj=item.report.sheet,
            action='UPDATE_COST_ITEM',
            changes={
                'item_id': item_id, 
                'amount_change': f"{old_amount} -> {item.amount}",
                'updated_fields': list(data.keys())
            },
            description=_(f"ویرایش آیتم هزینه")
        )
        return item

    # ============ ITEM DELETE ============ #
    @transaction.atomic
    def delete_report_item(self, user: User, item_id: int) -> None:
        AppPermissionChecker.check_has_permission(user, 'change_ordercostreport')

        item = OrderFinancialItem.objects.get_by_id(item_id)
        if not item: raise ValidationError("آیتم یافت نشد.")
        # ===== اعتبارسنجی ===== #
        self._domain_service.validate_item_modification(item.report)
        sheet = item.report.sheet
        deleted_amount = str(item.amount)
        # ===== حذف ===== #
        item.delete()
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

    # ============ SHEET CREATE ============ #
    @transaction.atomic
    def create_sheet(self, user: User, order_id: int) -> OrderFinancialSheet:
        """
        ایجاد دستی سند مالی (Ledger) برای یک سفارش.
        """
        AppPermissionChecker.check_has_permission(user, 'add_ordercostsheet')
        # ===== بررسی تکراری نبودن ===== #
        if OrderFinancialSheet.objects.get_by_order_id(order_id):
            raise ValidationError("سند مالی برای این سفارش قبلاً ایجاد شده است.")
        # ===== بررسی وجود سفارش ===== #
        if not Order.objects.filter(id=order_id).exists():
             raise ValidationError("سفارش مورد نظر یافت نشد.")
        # ===== ایجاد ===== #
        sheet = OrderFinancialSheet.objects.create(order_id=order_id)

        # ===== ثبت لاگ ===== #
        self.audit_service.record_log(
            user=user,
            obj=sheet,
            action='CREATE_COST_SHEET',
            description=_(f"افتتاح سند مالی سفارش")
        )
        return sheet

    # ============ SHEET UPDATE ============ #
    @transaction.atomic
    def update_sheet(self, user: User, sheet_id: int, data: Dict[str, Any]) -> OrderFinancialSheet:
        """
        ویرایش اطلاعات کلی سند مالی.
        """
        AppPermissionChecker.check_has_permission(user, 'change_ordercostsheet')
        # ===== بازیابی سند ===== #
        sheet = OrderFinancialSheet.objects.get_by_id(sheet_id)
        if not sheet:
            raise ValidationError("سند مالی یافت نشد.")
        # ===== ویرایش ===== #
        for key, value in data.items():
            setattr(sheet, key, value)
        sheet.save()
        # ===== محاسبه مجدد ===== #
        self._domain_service.recalculate_sheet_totals(sheet)
        
        return sheet

    @transaction.atomic
    def delete_sheet(self, user: User, sheet_id: int) -> None:
        """
        حذف سند مالی.
        قانون بیزنس: سندی که دارای گزارش تایید شده (گردش مالی) باشد، نباید حذف شود.
        """
        AppPermissionChecker.check_has_permission(user, 'delete_ordercostsheet')
        # ===== بازگیری سند ===== #
        sheet = OrderFinancialSheet.objects.get_by_id(sheet_id)
        if not sheet:
            raise ValidationError("سند مالی یافت نشد.")
        # ===== بررسی تکراری ===== #
        has_approved_reports = sheet.reports.filter(status='approved').exists()
        if has_approved_reports:
             raise ValidationError("این سند دارای گزارش‌های تایید شده است و قابل حذف نیست. ابتدا گزارش‌ها را رد/حذف کنید.")
        # ===== حذف ===== #
        order_code = sheet.order.order_code if sheet.order else "Unknown"
        sheet.delete()
        # ===== ثبت لاگ حذف ===== #
        self.audit_service.record_log(
            user=user,
            obj=None,
            action='DELETE_COST_SHEET',
            changes={'deleted_sheet_id': sheet_id, 'order_code': order_code},
            description=_(f"حذف سند مالی سفارش")
        )
    
    # =========== SHEET GET =========== #
    def get_order_cost_sheet(self, user: User, order_id: int) -> OrderFinancialSheet:
        """ 
        مشاهده سند کل بهای تمام شده سفارش.
        """
        AppPermissionChecker.check_has_permission(user, 'view_ordercostsheet')
        
        sheet = OrderFinancialSheet.objects.get_by_order_id(order_id)
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
    def lock_order_costs(self, user: User, order_id: int) -> OrderFinancialSheet:
        """
        قفل کردن حساب سفارش
        """
        AppPermissionChecker.check_has_permission(user, 'lock_ordercostsheet')
        return self._domain_service.lock_cost_sheet(order_id, user)

    # ========== INTERNAL METHODS ========== #
    def _ensure_sheet_exists(self, order_id: int) -> OrderFinancialSheet:
        sheet = OrderFinancialSheet.objects.get_by_order_id(order_id)
        if not sheet:
            if not Order.objects.filter(id=order_id).exists():
                raise ValidationError("سفارش یافت نشد.")
            sheet = OrderFinancialSheet.objects.create(order_id=order_id)
        return sheet

    def _bulk_create_items(self, report: OrderFinancialReport, items_data: List[Dict]):
        """Helper to create multiple items at once"""
        new_items = []
        for item_data in items_data:
            category = None
            if item_data.get('category_id'):
                category = OrderFinancialCategory.objects.get_by_id(item_data['category_id'])
            
            new_items.append(OrderFinancialItem(
                report=report,
                category=category,
                custom_title=item_data.get('custom_title'),
                amount=item_data.get('amount', 0),
                description=item_data.get('description', '')
            ))
        
        if new_items:
            OrderFinancialItem.objects.bulk_create_items(new_items)
    
    def _create_attachments(self, report: OrderFinancialReport, files: List[UploadedFile]):
        """Helper to create attachments"""
        attachments = []
        for file in files:
            OrderFinancialAttachment.objects.create(report=report, file=file, title=file.name)


    # ========== REVENUE ========== #
    # ========== CREATE REVENUE REPORT (FINANCE ONLY) ========== #
    @transaction.atomic
    def create_revenue_report(self, user: User, order_id: int, data: Dict, items: List[Dict] = [], attachments: List[UploadedFile] = []) -> OrderFinancialReport:
        """
        ایجاد گزارش درآمد توسط واحد مالی.
        چرایی: این متد برخلاف واحدها، ماهیت را روی 'revenue' تنظیم می‌کند.
        """
        AppPermissionChecker.check_has_permission(user, 'add_orderfinancialreport')
        
        # ===== اطمینان از وجود سند و بررسی قفل نبودن ===== #
        sheet = self._ensure_sheet_exists(order_id)
        self._domain_service._validate_sheet_is_modifiable(sheet)
        
        financial_tag = None
        if data.get("financial_tag_id"):
            financial_tag = OrderFinancialType.objects.get(id=data.get("financial_tag_id"))

        # ===== ایجاد هدر گزارش با ماهیت درآمد ===== #
        report = OrderFinancialReport.objects.create(
            sheet=sheet,
            submitter=user,
            financial_tag=financial_tag,
            title=data["title"],
            nature='revenue',
            description=data.get("description", ""),
            is_approved=False
        )
        
        # ===== ایجاد اقلام و پیوست‌ها ===== #
        if items:
            self._bulk_create_items(report, items)
        if attachments:
            self._create_attachments(report, attachments)
        
        # ===== محاسبه مجدد تراز مالی سفارش ===== #
        self._domain_service.recalculate_sheet_totals(sheet)
        
        # ===== ثبت لاگ سیستم ===== #
        self.audit_service.record_log(
            user=user,
            obj=report.sheet,
            action='CREATE_REVENUE',
            changes={'report_id': report.id, 'nature': 'revenue'},
            description=_(f"ثبت گزارش درآمد جدید: {report.title}")
        )
        return report

    # ===== DELETE SINGLE REVENUE REPORT ===== #
    @transaction.atomic
    def delete_revenue_report(self, user: User, order_id: int, report_id: int) -> None:
        AppPermissionChecker.check_has_permission(user, 'delete_orderfinancialreport')
        
        # ===== دریافت گزارش ===== #
        report = OrderFinancialReport.objects.get_by_order_and_id(order_id, report_id)
        
        if not report or report.nature != 'revenue':
            raise ValidationError("گزارش درآمدی با این مشخصات یافت نشد.")

        sheet = report.sheet
        report_title = report.title
        
        # ===== حذف گزارش ===== #
        report.delete()
        self._domain_service.recalculate_sheet_totals(sheet)

        self.audit_service.record_log(
            user=user,
            obj=sheet,
            action='DELETE_REVENUE',
            changes={'deleted_report_id': report_id, 'order_id': order_id, 'title': report_title},
            description=_(f"حذف گزارش درآمد: {report_title}")
        )

    # ===== DECIDE ON REVENUE REPORT ===== #
    def decide_on_revenue(self, user: User, report_id: int, approve: bool) -> OrderFinancialReport:
        """
        تایید یا رد گزارش درآمد توسط واحد مالی.
        چرایی: مشابه هزینه‌ها، هر درآمدی باید قابلیت تایید یا رد شدن برای نشستن در حساب سفارش را داشته باشد.
        """
        AppPermissionChecker.check_has_permission(user, 'approve_orderfinancialreport')
        
        # اطمینان از اینکه گزارش حتماً از نوع درآمد (revenue) باشد
        report = OrderFinancialReport.objects.filter(id=report_id, nature='revenue').first()
        if not report:
            raise ValidationError("گزارش درآمدی مورد نظر یافت نشد.")

        if approve:
            return self._domain_service.approve_report(report_id, user)
        else:
            return self._domain_service.reject_report(report_id, user)

    # ===== GET REVENUE DETAIL ===== #
    def get_revenue_detail(self, user: User, order_id: int, report_id: int) -> OrderFinancialReport:
        AppPermissionChecker.check_has_permission(user, 'view_orderfinancialreport')
        
        report = OrderFinancialReport.objects.get_by_order_and_id(order_id, report_id)
        
        if not report or report.nature != 'revenue':
            raise ValidationError("گزارش درآمد مورد نظر یافت نشد.")
        return report

    # ===== BULK DELETE REPORTS ===== #
    @transaction.atomic
    def bulk_delete_reports(self, user: User, report_ids: List[int]) -> None:
        """
        حذف دسته‌جمعی گزارش‌ها.
        چرایی: مالی نیاز دارد گاهی چندین گزارش اشتباه را با هم حذف کند.
        """
        AppPermissionChecker.check_has_permission(user, 'delete_orderfinancialreport')
        
        reports = OrderFinancialReport.objects.filter(id__in=report_ids)
        if not reports.exists():
            return

        sheets_to_update = list(reports.values_list('sheet_id', flat=True).distinct())
        
        # ===== حذف فیزیکی ===== #
        reports.delete()

        # ===== بروزرسانی شیت‌های متاثر از حذف ===== #
        for sheet_id in sheets_to_update:
            sheet = OrderFinancialSheet.objects.get(id=sheet_id)
            self._domain_service.recalculate_sheet_totals(sheet)

        self.audit_service.record_log(
            user=user,
            obj=None,
            action='BULK_DELETE_REPORTS',
            changes={'count': len(report_ids)},
            description=_("حذف دسته‌جمعی گزارش‌های مالی")
        )
