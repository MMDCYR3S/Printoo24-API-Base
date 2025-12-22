from datetime import datetime
from typing import Optional, Dict, Any, List

from django.db import models
from django.db.models import Prefetch, Q, Count, Max
from .base import BaseQuerySet

# ========== PRODUCT QUERYSET ========== #
class ProductQuerySet(BaseQuerySet):
    """
    کوئری‌های مربوط به مدل Product
    """

    # ===== Internal Helpers ===== #
    def _get_detail_queryset(self):
        """
        یک کوئری‌ست پایه و سنگین که تمام روابط مورد نیاز را بارگذاری می‌کند (Eager Loading).
        """
        # ===== ایمپورت محلی برای جلوگیری از خطا ===== #
        from core.product.models import (
            ProductQuantity, ProductSize, ProductOption, 
            ProductOptionValue, ProductImage, ProductAttachment
        )

        return self.select_related(
            'category',
            'pricing_config'
        ).prefetch_related(
            # ===== بارگذاری مقادیر ثابت ===== #
            Prefetch('product_quantity', queryset=ProductQuantity.objects.select_related('quantity').order_by('quantity__value')),
            Prefetch('product_size', queryset=ProductSize.objects.select_related('size').order_by('size__width')),
            
            # ===== بارگذاری ویژگی ها ===== #
            Prefetch(
                'options', 
                queryset=ProductOption.objects.select_related('option').prefetch_related(
                    Prefetch(
                        'choices', 
                        queryset=ProductOptionValue.objects.order_by('order')
                    )
                ).order_by('order')
            ),
            
            # ===== بارگذاری تصاویر و فایل های پیوست ===== #
            Prefetch('product_image', queryset=ProductImage.objects.order_by('order')),
            Prefetch('product_attachment_product', queryset=ProductAttachment.objects.order_by('id')),
        )

    def _get_optimized_queryset(self):
        """
        کوئری‌ست پایه با بارگذاری روابط اصلی (بدون آپشن‌ها و فایل‌ها).
        """
        from ..models import ProductQuantity, ProductImage
        return self.select_related(
            'category',
            'pricing_config'
        ).prefetch_related(
            Prefetch(
                'product_quantity', 
                queryset=ProductQuantity.objects.select_related('quantity').order_by('quantity__value')
            ),
            Prefetch('product_image', queryset=ProductImage.objects.order_by('order')),
        )

    # ===== Read Methods ===== #
    def get_all_active(self):
        """دریافت لیست تمام محصولات فعال"""
        return self.filter(is_active=True).select_related('category')
    
    def get_all(self):
        """دریافت تمام محصولات"""
        return self.select_related('category').order_by('-created_at')

    def get_by_category_ids(self, category_ids: list):
        """دریافت محصولات فعال بر اساس لیست دسته‌بندی‌ها"""
        return self.filter(
            category_id__in=category_ids, 
            is_active=True
        ).select_related('category').prefetch_related('product_image').order_by('-created_at')

    def get_detail_by_slug(self, slug: str):
        """دریافت جزئیات کامل با اسلاگ"""
        try:
            return self._get_detail_queryset().get(slug=slug, is_active=True)
        except self.model.DoesNotExist:
            return None

    def get_detail_by_id(self, id: int):
        """دریافت جزئیات کامل با ID"""
        return self._get_detail_queryset().get(pk=id)

    # ===== Stats Methods ===== #
    def get_count_by_date_range(self, start_date: datetime, end_date: datetime) -> int:
        return self.filter(created_at__range=(start_date, end_date)).count()

    def get_status_breakdown(self) -> dict:
        return self.aggregate(
            active=Count('id', filter=Q(is_active=True)),
            inactive=Count('id', filter=Q(is_active=False))
        )

    def get_quantity_status_breakdown(self) -> dict:
        return self.aggregate(
            with_quantity=Count('id', filter=Q(has_quantity=True)),
            without_quantity=Count('id', filter=Q(has_quantity=False))
        )


# ========== PRODUCT MANAGER ========== #
class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

    def get_all_active_products(self):
        return self.get_queryset().get_all_active()
    
    def get_all(self):
        return self.get_queryset().get_all()
    
    def get_all_products(self):
        return self.get_queryset().get_all()

    def get_products_by_category_ids(self, category_ids: list):
        return self.get_queryset().get_by_category_ids(category_ids)

    def get_product_detail_by_slug(self, slug: str):
        return self.get_queryset().get_detail_by_slug(slug)
    
    def get_product_detail_by_id(self, id: int):
        # اینجا اکسپشن DoesNotExist مدل رایز می‌شود اگر نباشد
        return self.get_queryset().get_detail_by_id(id)

    def get_by_id(self, pk: int):
        return self.get_queryset().get_by_id(pk)

    # ===== متد های مربوط به داشبورد ===== #
    def get_total_count(self) -> int:
        return self.count()

    def get_count_by_date_range(self, start: datetime, end: datetime):
        return self.get_queryset().get_count_by_date_range(start, end)

    def get_status_breakdown(self):
        return self.get_queryset().get_status_breakdown()

    def get_quantity_status_breakdown(self):
        return self.get_queryset().get_quantity_status_breakdown()
