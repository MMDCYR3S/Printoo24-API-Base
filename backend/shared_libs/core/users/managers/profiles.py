from django.db import models
from .base import BaseQuerySet

# ===== Customer Profile QuerySet ===== #
class CustomerProfileQuerySet(BaseQuerySet):
    """
    کوئری‌های مربوط به پروفایل مشتری
    """
    
    def get_by_user_id(self, user_id: int):
        """
        دریافت پروفایل کاربر با استفاده از ID کاربر
        """
        return self.filter(user_id=user_id).first()

    def get_by_username(self, username: str):
        """
        دریافت پروفایل بر اساس نام کاربری
        """
        return self.filter(user__username=username).first()


# ===== Customer Profile Manager ===== #
class CustomerProfileManager(models.Manager):
    """
    مدیر مدل پروفایل مشتری
    """
    def get_queryset(self):
        return CustomerProfileQuerySet(self.model, using=self._db)

    def get_by_user_id(self, user_id: int):
        return self.get_queryset().get_by_user_id(user_id)

    def get_by_username(self, username: str):
        return self.get_queryset().get_by_username(username)
