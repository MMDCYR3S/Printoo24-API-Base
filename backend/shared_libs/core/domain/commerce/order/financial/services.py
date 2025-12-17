from django.db import transaction
from django.core.exceptions import ValidationError

from core.models import (
    User, OrderCostSheet, OrderCostReport, 
)
from .repositories import (
    OrderCostSheetRepository, OrderCostReportRepository, 
)

# ============ ORDER COST DOMAIN SERVICE ============ #
class OrderCostDomainService:
    def __init__(self):
        self.sheet_repo = OrderCostSheetRepository()
        self.report_repo = OrderCostReportRepository()

    # ============ BUSINESS LOGIC & STATE TRANSITIONS ============ #
    @transaction.atomic
    def approve_report(self, report_id: int, approver: User) -> OrderCostReport:
        """
        تایید نهایی گزارش هزینه
        قانون: سند مادر نباید قفل باشد. گزارش نباید قبلا تایید شده باشد.
        ساید افکت: بعد از تایید، وضعیت تغییر کرده و محاسبات سند مادر بروز می‌شود.
        """
        report = self.report_repo.get_report_detail(report_id)
        if not report:
            raise ValidationError("گزارش یافت نشد.")

        # ===== اعمال قوانین ===== #
        self._validate_sheet_is_modifiable(report.sheet)
        
        if report.is_approved:
            raise ValidationError("این گزارش قبلاً تایید شده است.")

        # ===== تغییر وضعیت ===== #
        report.is_approved = True
        report.save()

        # ===== بروزرسانی سبد مادر ===== #
        self.recalculate_sheet_totals(report.sheet)
        
        return report
    
    @transaction.atomic
    def reject_report(self, report_id: int, user: User) -> OrderCostReport:
        """
        رد کردن گزارش هزینه.
        ساید افکت: اگر گزارش قبلا تایید شده بود و حالا رد شود، باید از محاسبات کسر شود.
        """
        report = self.report_repo.get_report_detail(report_id)
        if not report:
            raise ValidationError("گزارش یافت نشد.")

        self._validate_sheet_is_modifiable(report.sheet)

        was_approved = report.is_approved
        
        # ===== تغییر وضعیت ===== #
        report.is_approved = False
        report.save()

        # ===== تغییر جمع ===== #
        if was_approved:
            self.recalculate_sheet_totals(report.sheet)

        return report

    @transaction.atomic
    def lock_cost_sheet(self, order_id: int, user: User) -> OrderCostSheet:
        """
        قفل کردن سند مالی.
        قانون: بعد از قفل شدن، هیچ تغییری در گزارش‌های زیرمجموعه مجاز نیست.
        ساید افکت: محاسبه نهایی تمام ارقام قبل از قفل کردن.
        """
        sheet = self.sheet_repo.get_by_order_id(order_id)
        if not sheet:
            raise ValidationError("سند مالی برای این سفارش یافت نشد.")
            
        if sheet.is_locked:
            raise ValidationError("این سند قبلاً قفل شده است.")

        # ===== محاسبه دوباره ===== #
        self.recalculate_sheet_totals(sheet)
        
        sheet.is_locked = True
        sheet.save()
        return sheet

    def recalculate_sheet_totals(self, sheet: OrderCostSheet) -> None:
        """
        فراخوانی منطق محاسبه مجدد در مدل.
        این متد باید توسط App Service بعد از هر تغییر CRUD (مثل افزودن آیتم یا حذف گزارش) صدا زده شود.
        """
        sheet.recalculate_totals()

    # ============ VALIDATION GUARDS (Business Rules Helpers) ============ #
    def validate_report_modification(self, report_id: int) -> OrderCostReport:
        """
        بررسی می‌کند که آیا امکان ویرایش یا حذف این گزارش وجود دارد؟
        این متد توسط App Service قبل از update/delete صدا زده می‌شود.
        """
        report = self.report_repo.get_report_detail(report_id)
        if not report:
            raise ValidationError("گزارش یافت نشد.")
            
        if report.is_approved:
            raise ValidationError("گزارش تایید شده قابل ویرایش/حذف نیست.")
            
        self._validate_sheet_is_modifiable(report.sheet)
        
        return report

    def validate_item_modification(self, report: OrderCostReport) -> None:
        """
        بررسی قوانین مربوط به تغییر اقلام (Items) داخل گزارش.
        """
        if report.is_approved:
            raise ValidationError("امکان تغییر اقلام در گزارش تایید شده وجود ندارد.")
        self._validate_sheet_is_modifiable(report.sheet)

    def _validate_sheet_is_modifiable(self, sheet: OrderCostSheet) -> None:
        """Internal helper"""
        if sheet.is_locked:
            raise ValidationError("سند مالی این سفارش قفل شده است و امکان تغییر وجود ندارد.")
    