from typing import Dict, Any, Optional
from django.db import models
from .base import BaseQuerySet

# ========== SIZE QUERYSET ========== #
class SizeQuerySet(BaseQuerySet):
    """
    کوئری‌های مربوط به سایز
    """
    def get_all_sizes(self):
        return self.order_by('name')

    def get_by_name(self, name: str):
        return self.filter(name=name).first()
    
    def get_by_id(self, pk: int):
        return self.filter(pk=pk).first()

# ========== SIZE MANAGERS ========== #
class SizeManager(models.Manager):
    def get_queryset(self):
        return SizeQuerySet(self.model, using=self._db)

    def get_all_sizes(self):
        return self.get_queryset().get_all_sizes()

    def get_by_name(self, name: str):
        return self.get_queryset().get_by_name(name)
    
    def get_by_id(self, pk: int):
        return self.get_queryset().get_by_id(pk)
    
    def create_size(self, data: Dict[str, Any]):
        return self.create(**data)

# ========== QUANTITY QUERYSET ========== #
class QuantityQuerySet(BaseQuerySet):
    """
    کوئری‌های مربوط به تیراژ
    """
    def get_all_quantities(self):
        return self.order_by('value')

    def get_by_value(self, value: int):
        return self.filter(value=value).first()
    
    def get_by_id(self, pk: int):
        return self.filter(pk=pk).first()

# ========== QUANTITY MANAGERS ========== #
class QuantityManager(models.Manager):
    def get_queryset(self):
        return QuantityQuerySet(self.model, using=self._db)

    def get_all_quantities(self):
        return self.get_queryset().get_all_quantities()

    def get_by_value(self, value: int):
        return self.get_queryset().get_by_value(value)
    
    def get_by_id(self, pk: int):
        return self.get_queryset().get_by_id(pk)

    def create_quantity(self, data: Dict[str, Any]):
        return self.create(**data)
