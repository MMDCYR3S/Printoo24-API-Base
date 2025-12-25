from typing import Optional
from core.order.models import OrderSchedule

class OrderScheduleService:
    """
    سرویس مدیریت زمان‌بندی سفارشات.
    """
    
    def get_schedule_by_order_id(self, order_id: int) -> Optional[OrderSchedule]:
        """ دریافت زمان‌بندی بر اساس شناسه سفارش """
        return OrderSchedule.objects.get_by_order_id(order_id)
