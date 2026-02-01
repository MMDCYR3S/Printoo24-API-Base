from typing import Optional
from django.db import models
from django.db.models import Count
from .base import BaseQuerySet

# ========== STATUS GROUP QUERYSET ========== #
class OrderStatusGroupQuerySet(BaseQuerySet):
    """کوئری‌های مربوط به گروه وضعیت"""
    
    def get_group_by_code(self, code: str):
        return self.filter(code=code).first()

    def get_all_groups_with_status_count(self):
        """ دریافت تمام گروه‌ها با تعداد وضعیت‌های مرتبط """
        return self.annotate(
            status_count=Count('order_status')
        ).order_by('id')
    
    def get_by_id(self, pk: int):
        return self.filter(pk=pk).first()

# ========== STATUS GROUP MANAGERS ========== #
class OrderStatusGroupManager(models.Manager):
    def get_queryset(self):
        return OrderStatusGroupQuerySet(self.model, using=self._db)

    def get_group_by_code(self, code: str):
        return self.get_queryset().get_group_by_code(code)

    def get_all_groups_with_status_count(self):
        return self.get_queryset().get_all_groups_with_status_count()
    
    def get_by_id(self, pk: int):
        return self.get_queryset().get_by_id(pk)
    
    def create_group(self, data):
        return self.create(**data)


# ========== STATUS QUERYSET ========== #
class OrderStatusQuerySet(BaseQuerySet):
    """کوئری‌های مربوط به وضعیت سفارش"""
    
    def get_status_by_code(self, internal_code: str):
        return self.filter(internal_code__icontains=internal_code).first()

    def get_status_with_group_detail(self, status_id: int):
        return self.select_related('group').filter(id=status_id).first()

    def get_all_statuses_with_details(self):
        return self.select_related('group').order_by('id')
    
    def get_by_id(self, pk: int):
        return self.filter(pk=pk).first()

# ========== STATUS MANAGERS ========== #
class OrderStatusManager(models.Manager):
    def get_queryset(self):
        return OrderStatusQuerySet(self.model, using=self._db)

    def get_status_by_code(self, internal_code: str):
        return self.get_queryset().get_status_by_code(internal_code)

    def get_status_with_group_detail(self, status_id: int):
        return self.get_queryset().get_status_with_group_detail(status_id)

    def get_all_statuses_with_details(self):
        return self.get_queryset().get_all_statuses_with_details()
    
    def get_by_id(self, pk: int):
        return self.get_queryset().get_by_id(pk)

    def check_for_active_orders(self, status) -> bool:
        """ بررسی می‌کند که آیا سفارشی در حال حاضر از این وضعیت استفاده می‌کند؟ """
        return status.orders.exists()
    
    def create_status(self, data):
        return self.create(**data)
