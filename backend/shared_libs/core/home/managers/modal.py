from django.db import models
from .base import BaseQuerySet

# ========== MODAL QUERYSET ========== #
class ModalQuerySet(BaseQuerySet):
    """کوئری‌های مربوط به مودال تبلیغاتی"""
    
    def get_active_modal(self):
        """دریافت مودال فعال (باید فقط یکی باشد)."""
        return self.filter(is_active=True).first()

    def get_all_modals(self):
        return self.order_by('-created_at')

# ========== MODAL MANAGER ========== #
class ModalManager(models.Manager):
    def get_queryset(self):
        return ModalQuerySet(self.model, using=self._db)

    def get_active_modal(self):
        return self.get_queryset().get_active_modal()

    def get_all_modals(self):
        return self.get_queryset().get_all_modals()
    
    def get_by_id(self, pk: int):
        return self.get_queryset().get_by_id(pk)
    
    def create_modal(self, data: dict):
        return self.create(**data)
        
    def deactivate_all(self):
        """غیرفعال کردن تمام مودال‌ها"""
        self.get_queryset().update(is_active=False)