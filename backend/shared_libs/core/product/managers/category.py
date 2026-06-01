from typing import Optional, List
from mptt.managers import TreeManager 
from mptt.querysets import TreeQuerySet

from django.db import models

from ..exceptions import ProductCategoryNotFoundException

# ========== CATEGORY QUERYSET ========== #
class ProductCategoryQuerySet(TreeQuerySet):
    """
    کوئری‌های اختصاصی برای دسته‌بندی‌ها (MPTT)
    """
    def get_all_active_categories(self):
        """
        دریافت تمام دسته‌بندی‌ها به صورت مرتب شده بر اساس ساختار درختی.
        """
        return self.filter(is_active=True).order_by('tree_id', 'lft')
    
    def get_subcategories_with_parent(self):
        return self.filter(
            parent__isnull=False,
            is_active=True
        ).select_related(
            'parent'
        ).order_by('parent__id', 'order', 'name')

    def get_root_categories(self):
        """
        دریافت فقط دسته‌بندی‌های والد (ریشه) که فعال هستند.
        """
        return self.filter(parent__isnull=True, is_active=True).order_by('order', 'tree_id')

    def get_by_slug(self, slug: str):
        """دریافت دسته‌بندی با اسلاگ (رایز کردن اکسپشن در سرویس یا اینجا)"""
        # طبق الگوی ریپازیتوری شما، اینجا باید رایز کند
        try:
            return self.get(slug=slug)
        except self.model.DoesNotExist:
             raise ProductCategoryNotFoundException(f"دسته‌بندی با اسلاگ '{slug}' یافت نشد.")

# ========== CATEGORY MANAGER ========== #
class ProductCategoryManager(TreeManager):
    """
    مدیر مدل دسته‌بندی (ارث‌بری از TreeManager برای پشتیبانی MPTT)
    """
    def get_queryset(self):
        return ProductCategoryQuerySet(self.model, using=self._db).order_by('tree_id', 'lft')

    def get_all_active_categories(self):
        return self.get_queryset().get_all_active_categories()
    
    def get_subcategories_with_parent(self):
        return self.get_queryset().get_subcategories_with_parent()

    def get_root_categories(self):
        return self.get_queryset().get_root_categories()

    def get_by_slug(self, slug: str):
        return self.get_queryset().get_by_slug(slug)
    
    def get_descendants_queryset(self, category):
        return category.get_descendants(include_self=True)
    
    # ========== BULK OPERATIONS ========== #
    def bulk_toggle_status(self, ids: List[int], is_active: bool):
        return self.filter(id__in=ids).update(is_active=is_active)

    def bulk_delete_categories(self, ids: List[int]):
        return self.filter(id__in=ids).delete()
