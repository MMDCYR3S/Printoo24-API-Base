from typing import List, Dict, Any, Optional

from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from core.models import User, Order, OrderItem, OrderStatus, OrderStatusGroup
from apps.support.services import LoggerService
from apps.order.models import *

# ========== COST SERVICE ========== #
class OrderCostService:
    """
    سرویس دامنه مدیریت هزینه‌های سفارش.
    """
    def __init__(self):
        self.audit_service = LoggerService()

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
        
        # ===== دریافت سفارش مربوطه ===== #
        order = report.sheet.order
        if not order:
            raise ValidationError("سفارش مرتبط با این گزارش یافت نشد.")

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

        # ===== تغییر وضعیت در صورت تایید تمامی گزارش‌ها ===== #
        has_pending_reports = order.cost_sheet.reports.filter(is_approved=False).exists()

        if not has_pending_reports:
            self._advance_order_status(order, approver)

        # ===== بروزرسانی سند مادر ===== #
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
        
    # ========== CHANGE ORDER STATUS ========== #
    def _advance_order_status(self, order: Order, user: User):
        """
        جابجایی خودکار وضعیت سفارش به مرحله بعد بر اساس sort_order
        """
        current_status = order.current_status
        
        if not current_status:
            return
        
        # ===== دریافت وضعیت بعدی ===== #
        next_status = OrderStatus.objects.filter(
            sort_order__gt=current_status.sort_order
        ).order_by('sort_order').first()

        # ===== اگر وضعیت بعدی بود، اون رو به وضعیت فعلی تغییر بده ===== #
        if next_status:
            old_status_name = current_status.name
            order.current_status = next_status
            order.save(update_fields=['current_status', 'updated_at'])

        self.audit_service.record_log(
            user=user,
            obj=order,
            action='AUTO_STATUS',
            changes={
                'from_status': old_status_name,
                'to_status': next_status.name,
                'reason': 'All cost reports approved'
            },
            description=_(f"تغییر خودکار وضعیت از {old_status_name} به {next_status.name} به دلیل تکمیل گزارش‌های هزینه")
        )


# ========== ORDER SCHEDULE SERVICE ========== #
class OrderScheduleService:
    """
    سرویس مدیریت زمان‌بندی سفارشات.
    """
    
    def get_schedule_by_order_id(self, order_id: int) -> Optional[OrderSchedule]:
        """ دریافت زمان‌بندی بر اساس شناسه سفارش """
        return OrderSchedule.objects.get_by_order_id(order_id)

# ========== Order Status Flow Service ========== #
class OrderStatusFlowService:
    """
    سرویس مدیریت وضعیت سفارش (Workflow Engine).
    مسئول تضمین صحت تغییر وضعیت و ثبت تاریخچه است.
    """
    def __init__(self):
        self.audit_service = LoggerService()
        
    @transaction.atomic
    def change_order_status(self, order: Order, new_status_code: str, user: User, description: str = None) -> Order:
        """
        تغییر وضعیت سفارش توسط کاربر یا سیستم.
        """
        # ===== بررسی اینکه آیا وضعیت جدید معتبر است ===== #
        new_status = OrderStatus.objects.get_status_by_code(new_status_code)
        if not new_status:
            raise ValidationError(f"کد وضعیت نامعتبر: {new_status_code}")
        
        # ===== جلوگیری از تکرار ===== #
        if order.current_status_id == new_status.id:
            return order
            
        # ===== اجرای تغییر وضعیت ===== #
        return self._perform_transition(order, new_status, user, description)

    @transaction.atomic
    def change_item_status(self, item_id: int, new_status_code: str, user: User, description: str = None) -> OrderItem:
        """
        تغییر وضعیت یک قلم کالا (مثلاً تایید طراحی کارت ویزیت).
        این متد اتوماتیک وضعیت سفارش مادر را هم آپدیت می‌کند.
        """
        try:
            item = OrderItem.objects.get(id=item_id)
        except OrderItem.DoesNotExist:
            raise ValidationError("آیتم سفارش یافت نشد.")

        new_status = OrderStatus.objects.get_status_by_code(new_status_code)
        if not new_status:
            raise ValidationError(f"کد وضعیت نامعتبر: {new_status_code}")
            

        if getattr(new_status, 'target_model', None) == 'order':
             raise ValidationError("این وضعیت مختص کل سفارش است و نمی‌تواند روی آیتم اعمال شود.")

        
        old_status = item.status 
        
        if old_status and getattr(old_status, 'internal_code', str(old_status)) == new_status_code:
            return item

        changes = {
            "field": "status",
            "from_id": old_status.id if hasattr(old_status, 'id') else None,
            "to_id": new_status.id,
            "from_title": getattr(old_status, 'title', str(old_status)),
            "to_title": new_status.name, # name در مدل OrderStatus
            "internal_code_change": f"{getattr(old_status, 'internal_code', str(old_status))} -> {new_status.internal_code}"
        }

        self.audit_service.record_log(
            user=user,
            obj=item,
            action='STATUS_CHANGE',
            changes=changes,
            description=description or _("تغییر وضعیت آیتم سفارش")
        )
        
        item.status = new_status 
        
        item.save(update_fields=['status', 'updated_at'])

        # 2. فراخوانی منطق تجمیع (Rollup) برای آپدیت سفارش مادر
        self._update_master_order_status(item.order, user)

        return item
    
    # ============ منطق هسته ============ #
    def _perform_transition(self, order: Order, new_status: OrderStatus, user: User, description: str = None):
        """ متد کمکی برای جلوگیری از تکرار کد در تغییر وضعیت سفارش """
        old_status = order.current_status
        
        # ===== محاسبه مدت زمان توقف در مرحله قبل ===== #
        last_log = self.audit_service.get_last_action_log(order, action='STATUS_CHANGE')
        
        duration_seconds = 0
        formatted_duration = "N/A"
        
        if last_log:
            delta = timezone.now() - last_log.timestamp
            duration_seconds = delta.total_seconds()
            formatted_duration = str(delta).split('.')[0]
        
        # ===== آماده‌سازی داده‌های لاگ ===== #
        changes_data = {
            "transition": "order_status_update",
            "from_status": {
                "id": old_status.id if old_status else None,
                "title": old_status.name if old_status else "آغاز فرایند", 
                "code": old_status.internal_code if old_status else None
            },
            "to_status": {
                "id": new_status.id,
                "title": new_status.name,
                "code": new_status.internal_code
            },
            "metrics": {
                "duration_seconds": int(duration_seconds),
                "duration_readable": formatted_duration
            }
        }

        # ===== ثبت لاگ ===== #
        self.audit_service.record_log(
            user=user,
            obj=order,
            action='STATUS_CHANGE',
            changes=changes_data,
            description=description or _(f"تغییر وضعیت سفارش به {new_status.name}")
        )

        # ===== آپدیت نهایی دیتابیس ===== #
        order.current_status = new_status
        order.save(update_fields=['current_status', 'updated_at'])
        
        return order

    def _update_master_order_status(self, order: Order, user: User):
        """
        منطق تجمیع وضعیت آیتم‌ها (Rollup Logic).
        """
        items = order.order_item_order.all()
        total_items = items.count()

        if total_items == 0:
            return

        target_code = None
        
        # ===== رد شدن آیتم ===== #
        if items.filter(status__status_type='reject').exists():
            target_code = 'ATTENTION_NEEDED'
            
        # ===== تایید شدن آیتم ===== #
        elif items.filter(status__internal_code='DELIVERED').count() == total_items:
            target_code = 'COMPLETED'
            
        elif items.filter(status__group__code='production').count() == total_items:
            target_code = 'IN_PRODUCTION'
        
        if not target_code:
            return

        new_master_status = OrderStatus.objects.get_status_by_code(target_code)
        
        if new_master_status and order.current_status_id != new_master_status.id:
            self._perform_transition(
                order=order, 
                new_status=new_master_status, 
                user=user, 
                description="بروزرسانی خودکار بر اساس وضعیت آیتم‌ها"
            )


# ===== Order Status Group Domain Service ===== #
class OrderStatusGroupService:
    """
    سرویس دامنه برای مدیریت گروه‌های وضعیت (OrderStatusGroup).
    """

    @transaction.atomic
    def create_group(self, data: Dict[str, Any]) -> OrderStatusGroup:
        code = data.get('code')
        if OrderStatusGroup.objects.get_group_by_code(code):
            raise ValidationError(f"گروه با کد سیستمی '{code}' قبلاً وجود دارد.")
        
        return OrderStatusGroup.objects.create_group(data)

    @transaction.atomic
    def update_group(self, group_id: int, data: Dict[str, Any]) -> OrderStatusGroup:
        group = OrderStatusGroup.objects.get_by_id(group_id)
        if not group:
            raise ValidationError("گروه وضعیت یافت نشد.")

        code = data.get('code')
        if code and code != group.code and OrderStatusGroup.objects.get_group_by_code(code):
            raise ValidationError(f"کد سیستمی '{code}' تکراری است.")

        # آپدیت دستی
        for key, value in data.items():
            setattr(group, key, value)
        group.save()
        return group

    def delete_group(self, group_id: int):
        group = OrderStatusGroup.objects.get_by_id(group_id)
        if not group:
            raise ValidationError("گروه وضعیت یافت نشد.")

        if group.order_status.exists():
            raise ValidationError("امکان حذف نیست. این گروه وضعیت به یک یا چند وضعیت سفارش متصل است.")
        group.delete()


# ========== Order Status Domain Service ========== #
class OrderStatusService:
    """
    سرویس دامنه برای مدیریت وضعیت‌های سفارش (Status CRUD).
    """

    @transaction.atomic
    def create_status(self, data: Dict[str, Any]) -> OrderStatus:
        code = data.get('internal_code')
        if OrderStatus.objects.get_status_by_code(code):
            raise ValidationError(f"کد سیستمی وضعیت '{code}' قبلاً وجود دارد.")
        
        return OrderStatus.objects.create_status(data)

    @transaction.atomic
    def update_status(self, status_id: int, data: Dict[str, Any]) -> OrderStatus:
        status_obj = OrderStatus.objects.get_by_id(status_id)
        if not status_obj:
            raise ValidationError("وضعیت یافت نشد.")

        code = data.get('internal_code')
        if code and code != status_obj.internal_code and OrderStatus.objects.get_status_by_code(code):
            raise ValidationError(f"کد سیستمی '{code}' تکراری است.")

        for key, value in data.items():
            setattr(status_obj, key, value)
        status_obj.save()
        return status_obj

    def delete_status(self, status_id: int):
        status_obj = OrderStatus.objects.get_status_with_group_detail(status_id)
        if not status_obj:
            raise ValidationError("وضعیت یافت نشد.")
            
        if OrderStatus.objects.check_for_active_orders(status_obj):
            raise ValidationError("امکان حذف نیست. حداقل یک سفارش فعال از این وضعیت استفاده می‌کند.")
            
        status_obj.delete()
