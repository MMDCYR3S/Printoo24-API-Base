from typing import Optional
from core.utils.base_repository import BaseRepository
from core.models import OrderSchedule

class OrderScheduleRepository(BaseRepository[OrderSchedule]):
    """
    ریپازیتوری مدیریت زمان‌بندی سفارش.
    """
    def __init__(self):
        super().__init__(OrderSchedule)

    def get_by_order_id(self, order_id: int) -> Optional[OrderSchedule]:
        """ دریافت زمان‌بندی بر اساس شناسه سفارش """
        return self.model.objects.filter(order_id=order_id).first()