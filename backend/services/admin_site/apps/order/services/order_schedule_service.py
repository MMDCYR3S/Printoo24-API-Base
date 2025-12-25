from rest_framework.exceptions import ValidationError, NotFound
from django.utils.translation import gettext_lazy as _

from core.models import User, Order
from apps.support.services import LoggerService
from apps.order.models import OrderSchedule
from apps.permissions import AppPermissionChecker

# ========== Order Schedule App Service ========== #
class OrderScheduleAppService:
    """
    سرویس مدیریت زمان‌بندی سفارشات.
    مسئولیت‌ها:
    - ایجاد، مشاهده، ویرایش و حذف زمان‌بندی (Schedule)
    - چک کردن دسترسی‌ها
    - ثبت لاگ تغییرات حساس (مثل تغییر تاریخ تحویل)
    """
    def __init__(self):
        self.audit_service = LoggerService()

    def get_schedule(self, requester: User, order_id: int) -> OrderSchedule:
        """ مشاهده زمان‌بندی """
        AppPermissionChecker.check_has_permission(requester, 'view_orderschedule')
        
        schedule = OrderSchedule.objects.get_by_order_id(order_id)
        if not schedule:
            raise NotFound("زمان‌بندی برای این سفارش ثبت نشده است.")
        return schedule

    def create_schedule(self, requester: User, order_id: int, data: dict) -> OrderSchedule:
        """ 
        ایجاد زمان‌بندی جدید.
        """
        AppPermissionChecker.check_has_permission(requester, 'add_orderschedule')
        # ===== دریافت سفارش ===== #
        try:
            order = Order.objects.get(pk=order_id)
        except Order.DoesNotExist:
            raise ValidationError("سفارش مورد نظر یافت نشد.")

        if hasattr(order, 'schedule'):
            raise ValidationError("برای این سفارش قبلاً زمان‌بندی ثبت شده است. از متد ویرایش استفاده کنید.")

        schedule = OrderSchedule.objects.create(order=order, **data)
        
        # ===== ثبت لاگ ===== #
        self.audit_service.record_log(
            user=requester,
            obj=order,
            action='CREATE_SCHEDULE',
            changes={
                'start_date': str(schedule.start_date),
                'due_date': str(schedule.due_date)
            },
            description=_(f"تنظیم زمان‌بندی اولیه برای سفارش {order.order_code}")
        )
        
        return schedule

    def update_schedule(self, requester: User, order_id: int, data: dict) -> OrderSchedule:
        """
        ویرایش زمان‌بندی موجود.
        """
        AppPermissionChecker.check_has_permission(requester, 'change_orderschedule')
        # ===== دریافت سفارش ===== #
        schedule = OrderSchedule.objects.get_by_order_id(order_id)
        if not schedule:
            raise NotFound("زمان‌بندی برای این سفارش وجود ندارد.")
        # ===== دریافت زمانبندی قدیمی ===== #
        old_due_date = schedule.due_date
        
        # ===== بروزرسانی ===== #
        for key, value in data.items():
            setattr(schedule, key, value)
        
        schedule.save()
        new_due_date = schedule.due_date
    
        # ===== ثبت لاگ حساس ===== #
        changes_log = {'updated_fields': list(data.keys())}
        if str(old_due_date) != str(new_due_date):
            changes_log['due_date_change'] = f"{old_due_date} -> {new_due_date}"
    
        self.audit_service.record_log(
            user=requester,
            obj=schedule.order,
            action='UPDATE_SCHEDULE',
            changes=changes_log,
            description=_(f"تغییر زمان‌بندی سفارش")
        )
        
        return schedule

    def delete_schedule(self, requester: User, order_id: int):
        """ حذف زمان‌بندی """
        AppPermissionChecker.check_has_permission(requester, 'delete_orderschedule')
        
        schedule = OrderSchedule.objects.get_by_order_id(order_id)
        if not schedule:
            raise NotFound("زمان‌بندی یافت نشد.")
        
        order_code = schedule.order.order_code
        schedule.delete()
        
        # ===== ثبت لاگ حذف ===== #
        self.audit_service.record_log(
            user=requester,
            obj=None,
            action='DELETE_SCHEDULE',
            changes={'order_code': order_code},
            description=_(f"حذف کامل زمان‌بندی سفارش {order_code}")
        )
