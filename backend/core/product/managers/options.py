from typing import List, Dict, Any
from django.db import models
from .base import BaseQuerySet

# ========== OPTION QUERYSET ========== #
class OptionQuerySet(BaseQuerySet):
    """
    کوئری‌های مربوط به ویژگی‌ها (Option)
    """
    def get_all_with_values(self):
        """
        دریافت تمام ویژگی‌ها همراه با مقادیرشان (برای جلوگیری از N+1).
        """
        return self.prefetch_related('global_values').all().order_by('-created_at')

    def get_by_name(self, name: str):
        return self.filter(name=name).first()
    
    def get_by_id(self, pk: int):
        return self.filter(pk=pk).first()

# ========== OPTION MANAGERS ========== #
class OptionManager(models.Manager):
    def get_queryset(self):
        return OptionQuerySet(self.model, using=self._db)

    def get_all_with_values(self):
        return self.get_queryset().get_all_with_values()

    def get_by_name(self, name: str):
        return self.get_queryset().get_by_name(name)

    def get_by_id(self, pk: int):
        return self.get_queryset().get_by_id(pk)
    
    def create_option(self, data: Dict[str, Any]):
        return self.create(**data)


# ========== OPTION VALUE QUERYSET ========== #
class OptionValueQuerySet(BaseQuerySet):
    """کوئری‌های مربوط به مقادیر ویژگی (OptionValue)"""
    pass

# ========== OPTION VALUE MANAGERS ========== #
class OptionValueManager(models.Manager):
    def get_queryset(self):
        return OptionValueQuerySet(self.model, using=self._db)

    def create_value(self, option, data: Dict[str, Any]):
        return self.create(option=option, **data)

    def bulk_create_values(self, values: List):
        self.bulk_create(values)

    def delete_by_option(self, option):
        """حذف تمام مقادیر یک ویژگی"""
        self.filter(option=option).delete()
