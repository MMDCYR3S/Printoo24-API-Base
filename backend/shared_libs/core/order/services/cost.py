from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from core.models import User
from core.order.models import OrderCostSheet, OrderCostReport
from core.domain.infrastructure.logger import AuditLogDomainService

# ========== COST SERVICE ========== #
class OrderCostService:
    """
    سرویس دامنه مدیریت هزینه‌های سفارش.
    """
    def __init__(self):
        self.audit_service = AuditLogDomainService()

    # ============ BUSINESS LOGIC & STATE TRANSITIONS ============ #
    @transaction.atomic
    def approve_report(self, report_id: int, approver: User) -> OrderCostReport:
        """
        تایید نهایی گزارش هزینه.
        """
        # ===== بررسی وجود ===== #
        report = OrderCostReport.objects.get_report_detail(report_id)
        if not report:
            raise ValidationError("گزارش یافت نشد.")

        self._validate_sheet_is_modifiable(report.sheet)
        
        if report.is_approved:
            raise ValidationError("این گزارش قبلاً تایید شده است.")

        self.audit_service.record_log(
            user=approver,
            obj=report.sheet,
            action='APPROVE',
            changes={
                'target': 'CostReport',
                'report_id': report.id,
                'report_title': report.title,
                'status_change': 'Pending -> Approved'
            },
            description=_(f"تایید گزارش هزینه: {report.title}")
        )

        # ===== تغییر وضعیت ===== #
        report.is_approved = True
        report.save()

        # ===== بروزرسانی سبد مادر ===== #
        self.recalculate_sheet_totals(report.sheet)
        
        return report

    @transaction.atomic
    def reject_report(self, report_id: int, user: User) -> OrderCostReport:
        """
        رد کردن گزارش هزینه و ثبت لاگ.
        """
        report = OrderCostReport.objects.get_report_detail(report_id)
        if not report:
            raise ValidationError("گزارش یافت نشد.")

        self._validate_sheet_is_modifiable(report.sheet)

        was_approved = report.is_approved
        
        # ===== ثبت لاگ ===== #
        self.audit_service.record_log(
            user=user,
            obj=report.sheet,
            action='REJECT',
            changes={
                'target': 'CostReport',
                'report_id': report.id,
                'report_title': report.title,
                'status_change': 'Approved -> Rejected' if was_approved else 'Pending -> Rejected'
            },
            description=_(f"رد کردن گزارش هزینه: {report.title}")
        )

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
        قفل کردن سند مالی و ثبت لاگ امنیتی.
        """
        sheet = OrderCostSheet.objects.get_by_order_id(order_id)
        if not sheet:
            raise ValidationError("سند مالی برای این سفارش یافت نشد.")
            
        if sheet.is_locked:
            raise ValidationError("این سند قبلاً قفل شده است.")

        # ===== ثبت لاگ ===== #
        final_total = getattr(sheet, 'final_total_cost', 0)

        self.audit_service.record_log(
            user=user,
            obj=sheet,
            action='LOCK',
            changes={'is_locked': True, 'final_total': str(final_total)},
            description=_("قفل نهایی سند مالی سفارش")
        )

        # ===== محاسبه و قفل ===== #
        self.recalculate_sheet_totals(sheet)
        sheet.is_locked = True
        sheet.save()
        
        return sheet

    def recalculate_sheet_totals(self, sheet: OrderCostSheet) -> None:
        """
        فراخوانی منطق محاسبه مجدد در مدل.
        """
        sheet.recalculate_totals()

    # ============ VALIDATION GUARDS (Business Rules Helpers) ============ #
    def validate_report_modification(self, report_id: int) -> OrderCostReport:
        """
        بررسی می‌کند که آیا امکان ویرایش یا حذف این گزارش وجود دارد؟
        """
        report = OrderCostReport.objects.get_report_detail(report_id)
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
