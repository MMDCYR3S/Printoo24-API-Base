from rest_framework.exceptions import PermissionDenied, ValidationError, NotFound
from core.models import User, Order, OrderSchedule
from core.domain.commerce.order import OrderRepository, OrderScheduleRepository
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
        return self.schedule_repo.create(data)

    def update_schedule(self, requester: User, order_id: int, data: dict) -> OrderSchedule:
        """
        ویرایش زمان‌بندی موجود.
        """
        AppPermissionChecker.check_has_permission(requester, 'change_orderschedule')
        
        schedule = self.schedule_repo.get_by_order_id(order_id)
        if not schedule:
            raise NotFound("زمان‌بندی برای این سفارش وجود ندارد.")
            
        return self.schedule_repo.update(schedule, data)

    def delete_schedule(self, requester: User, order_id: int):
        """ حذف زمان‌بندی """
        AppPermissionChecker.check_has_permission(requester, 'delete_orderschedule')
        
        schedule = self.schedule_repo.get_by_order_id(order_id)
        if not schedule:
            raise NotFound("زمان‌بندی یافت نشد.")
            
        schedule.delete()
