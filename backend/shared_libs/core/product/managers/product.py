from datetime import datetime
from django.db import models
from django.db.models import Prefetch, Q, Count
from .base import BaseQuerySet

# ========== PRODUCT QUERYSET ========== #
class ProductQuerySet(BaseQuerySet):
    """
    کوئری‌های مربوط به مدل Product با معماری جدید فیلدساز و فرمول‌ساز
    """

    def _get_detail_queryset(self):
        """
        کوئری‌ست پایه برای دریافت جزئیات کامل محصول همراه با تمام فیلدها، شروط و فرمول‌ها (Eager Loading).
        """
        from core.product.models import (
            ProductField, ProductFieldChoice, ProductFieldCondition,
            ProductFormula, ProductImage, Attachment
        )

        return self.prefetch_related(
            'categories',
            # ===== بارگذاری فیلدها، گزینه‌ها و شروط وابستگی (Form Builder) ===== #
            Prefetch(
                'fields', 
                queryset=ProductField.objects.prefetch_related(
                    Prefetch('choices', queryset=ProductFieldChoice.objects.order_by('order')),
                    # 🌟 اصلاح شد: استفاده از نام صحیح related_name که در مدل تعریف شده است
                    Prefetch('applied_conditions', queryset=ProductFieldCondition.objects.all())
                ).order_by('order')
            ),
            # ===== بارگذاری فرمول‌های قیمت‌گذاری (Formula Builder) ===== #
            Prefetch('formulas', queryset=ProductFormula.objects.all()),
            # ===== بارگذاری تصاویر و فایل های پیوست ===== #
            Prefetch('product_image', queryset=ProductImage.objects.order_by('order')),
            Prefetch('product_attachment', queryset=Attachment.objects.all())
        )

    def _get_optimized_queryset(self):
        """
        کوئری‌ست سبک برای لیست محصولات (بدون لود کردن فیلدها و شروط سنگین).
        """
        from core.product.models import ProductImage
        return self.prefetch_related(
            'categories',
            Prefetch('product_image', queryset=ProductImage.objects.order_by('order'))
        )

    # ===== Read Methods ===== #
    def get_all_active(self):
        return self._get_optimized_queryset().filter(is_active=True)
    
    def get_all(self):
        return self._get_optimized_queryset().order_by('-created_at')

    def get_by_category_ids(self, category_ids: list):
        return self._get_optimized_queryset().filter(
            categories__id__in=category_ids, 
            is_active=True
        ).distinct().order_by('-created_at')

    def get_detail_by_slug(self, slug: str):
        try:
            return self._get_detail_queryset().get(slug=slug, is_active=True)
        except self.model.DoesNotExist:
            return None

    def get_detail_by_id(self, id: int):
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
    

    
    def search(self, query: str):
        """
        جستجو بر اساس نام، توضیحات، کد و نام/مقادیر فیلدساز جدید
        """
        if not query:
            return self.none()

        return self.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(code__icontains=query) |
            Q(fields__title__icontains=query) |           # جستجو در نام فیلدهای داینامیک
            Q(fields__choices__title__icontains=query)    # جستجو در گزینه‌های فیلدهای انتخابی
        ).filter(is_active=True).distinct()


# ========== PRODUCT MANAGER ========== #
class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

    def get_all_active_products(self):
        return self.get_queryset().get_all_active()
    
    def get_all(self):
        return self.get_queryset().get_all()

    def get_products_by_category_ids(self, category_ids: list):
        return self.get_queryset().get_by_category_ids(category_ids)

    def get_product_detail_by_slug(self, slug: str):
        return self.get_queryset().get_detail_by_slug(slug)
    
    def get_product_detail_by_id(self, id: int):
        return self.get_queryset().get_detail_by_id(id)

    def get_by_id(self, pk: int):
        return self.get_queryset().get_detail_by_id(pk)

    # ===== Dashboard Stats ===== #
    def get_total_count(self) -> int:
        return self.count()

    def get_count_by_date_range(self, start: datetime, end: datetime):
        return self.get_queryset().get_count_by_date_range(start, end)

    def get_status_breakdown(self):
        return self.get_queryset().get_status_breakdown()
    
    def get_quantity_status_breakdown(self):
        return self.get_queryset().get_quantity_status_breakdown()