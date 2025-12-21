from django.db import models
from .base import BaseQuerySet

# ========== SCHEDULE QUERYSET ========== #
class OrderScheduleQuerySet(BaseQuerySet):
    """
    کوئری‌های مربوط به زمان‌بندی سفارش
    """
    def get_by_order_id(self, order_id: int):
        """ دریافت زمان‌بندی بر اساس شناسه سفارش """
        return self.filter(order_id=order_id).first()

# ========== SCHEDULE MANAGER ========== #
class OrderScheduleManager(models.Manager):
    def get_queryset(self):
        return OrderScheduleQuerySet(self.model, using=self._db)

    def get_by_order_id(self, order_id: int):
        return self.get_queryset().get_by_order_id(order_id)