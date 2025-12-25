from django.db import models
from .base import BaseQuerySet

# ========== SLIDER QUERYSET ========== #
class SliderQuerySet(BaseQuerySet):
    """کوئری‌های مربوط به اسلایدر"""
    
    def get_all_sliders(self):
        return self.order_by('-created_at')

# =========== SLIDER MANAGER ========== #
class SliderManager(models.Manager):
    def get_queryset(self):
        return SliderQuerySet(self.model, using=self._db)

    def get_all_sliders(self):
        return self.get_queryset().get_all_sliders()
    
    def get_by_id(self, pk: int):
        return self.get_queryset().get_by_id(pk)
        
    def create_slider(self, data: dict):
        return self.create(**data)
