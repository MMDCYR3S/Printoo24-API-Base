from django.db import models
from .base import BaseQuerySet

# ========== CONTACT QUERYSET ========== #
class ContactUsQuerySet(BaseQuerySet):
    """کوئری‌های مربوط به تماس با ما"""
    
    def get_unread_messages(self):
        return self.filter(is_read=False)

# ========== CONTACT MANAGER ========== #
class ContactUsManager(models.Manager):
    def get_queryset(self):
        return ContactUsQuerySet(self.model, using=self._db)

    def create_message(self, data: dict):
        return self.create(**data)

    def get_unread_messages(self):
        return self.get_queryset().get_unread_messages()
    
    def get_by_id(self, pk: int):
        return self.get_queryset().get_by_id(pk)