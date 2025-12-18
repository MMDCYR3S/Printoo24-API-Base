from rest_framework.exceptions import PermissionDenied, ValidationError, NotFound
from django.utils.translation import gettext_lazy as _

from core.models import User, Order, OrderSchedule
from core.domain.commerce.order import OrderRepository, OrderScheduleRepository
from core.domain.infrastructure.logger.services import AuditLogDomainService
from apps.permissions import AppPermissionChecker

# ========== Order Schedule App Service ========== #
class OrderScheduleAppService:
    """
    سرویس مدیریت زمان‌بندی سفارشات.
    امنیت بر اساس پرمیشن‌های استاندارد (view, add, change, delete) روی مدل OrderSchedule.
    """
    def __init__(self):
        self.order_repo = OrderRepository()
        self.schedule_repo = OrderScheduleRepository()
        self.audit_service = AuditLogDomainService()

    def get_schedule(self, requester: User, order_id: int) -> OrderSchedule:
        """ مشاهده زمان‌بندی """
        AppPermissionChecker.check_has_permission(requester, 'view_orderschedule')
        
        schedule = self.schedule_repo.get_by_order_id(order_id)
        if not schedule:
            raise NotFound("زمان‌بندی برای این سفارش ثبت نشده است.")
        return schedule

    def create_schedule(self, requester: User, order_id: int, data: dict) -> OrderSchedule:
        """ 
        ایجاد زمان‌بندی جدید.
        """
        AppPermissionChecker.check_has_permission(requester, 'add_orderschedule')

        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise ValidationError("سفارش مورد نظر یافت نشد.")

        if hasattr(order, 'schedule'):
            raise ValidationError("برای این سفارش قبلاً زمان‌بندی ثبت شده است. از متد ویرایش استفاده کنید.")

        data['order'] = order
        schedule = self.schedule_repo.create(data)
        
        # ===== ثبت لاگ ===== #
        self.audit_service.record_log(
            user=requester,
            obj=order, # لاگ روی سفارش ثبت می‌شود (مهم‌تر از خود آبجکت اسکجول است)
            action='CREATE_SCHEDULE',
            changes={
                'production_start': str(schedule.production_start_date),
                'delivery_date': str(schedule.expected_delivery_date)
            },
            description=_(f"تنظیم زمان‌بندی اولیه برای سفارش {order.order_code}")
        )
        
        return schedule

    def update_schedule(self, requester: User, order_id: int, data: dict) -> OrderSchedule:
        """
        ویرایش زمان‌بندی موجود.
        """
        AppPermissionChecker.check_has_permission(requester, 'change_orderschedule')
        
        schedule = self.schedule_repo.get_by_order_id(order_id)
        if not schedule:
            raise NotFound("زمان‌بندی برای این سفارش وجود ندارد.")
        
        old_delivery = schedule.expected_delivery_date
        updated_schedule = self.schedule_repo.update(schedule, data)
        new_delivery = updated_schedule.expected_delivery_date
        
        # ===== ثبت لاگ حساس ===== #
        changes_log = {'updated_fields': list(data.keys())}
        if old_delivery != new_delivery:
            changes_log['delivery_date_change'] = f"{old_delivery} -> {new_delivery}"
    
        self.audit_service.record_log(
            user=requester,
            obj=updated_schedule.order,
            action='UPDATE_SCHEDULE',
            changes=changes_log,
            description=_(f"تغییر زمان‌بندی سفارش")
        )

    def delete_schedule(self, requester: User, order_id: int):
        """ حذف زمان‌بندی """
        AppPermissionChecker.check_has_permission(requester, 'delete_orderschedule')
        
        schedule = self.schedule_repo.get_by_order_id(order_id)
        if not schedule:
            raise NotFound("زمان‌بندی یافت نشد.")
        
        order_code = schedule.order.order_code
        self.schedule_repo.delete(schedule)
        
        # ===== ثبت لاگ حذف ===== #
        self.audit_service.record_log(
            user=requester,
            obj=None,
            action='DELETE_SCHEDULE',
            changes={'order_code': order_code},
            description=_(f"حذف کامل زمان‌بندی سفارش {order_code}")
        )
