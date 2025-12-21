from django.db import models
from .base import BaseQuerySet

# ===== Role QuerySet ===== #
class RoleQuerySet(BaseQuerySet):
    """
    جایگزین کوئری‌های RoleRepository
    """
    def get_all_roles(self):
        """لیست همه نقش‌ها با پرفورمنس بالا"""
        return self.prefetch_related('permission').order_by('id')

    def get_by_slug(self, slug: str):
        """دریافت نقش بر اساس اسلاگ"""
        return self.filter(slug=slug).first()

# ===== Role Manager ===== #
class RoleManager(models.Manager):
    def get_queryset(self):
        return RoleQuerySet(self.model, using=self._db)

    def get_all_roles(self):
        return self.get_queryset().get_all_roles()

    def get_role_by_slug(self, slug: str):
        return self.get_queryset().get_by_slug(slug)
        
    def get_by_id(self, id: int):
        return self.get_queryset().get_by_id(id)