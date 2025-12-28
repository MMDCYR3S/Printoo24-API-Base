from typing import Dict, Any, List, Optional
from django.db import transaction
from django.db.models import QuerySet

from ..models import ProductCategory, Product
from ..exceptions import ProductCategoryNotFoundException

# ========== CATEGORY SERVICE ========== #
class ProductCategoryService:
    """
    سرویس دامنه دسته‌بندی محصولات.
    """
    
    # ===== Read Operations ===== #
    def get_root_categories(self) -> QuerySet[ProductCategory]:
        """
        دریافت فقط دسته‌بندی‌های والد (ریشه) که فعال هستند.
        """
        return ProductCategory.objects.get_root_categories()
    
    def get_category_tree_queryset(self) -> QuerySet[ProductCategory]:
        """
        فقط کوئری‌ست را برمی‌گرداند. تبدیل به درخت وظیفه لایه نمایش است.
        """
        return ProductCategory.objects.get_all_active_categories()

    def get_all_active_categories(self):
        """ دریافت تمامی دسته‌های فعال """
        return ProductCategory.objects.get_all_active_categories()

    def get_category_by_slug(self, slug: str) -> Optional[ProductCategory]:
        """
        دریافت دسته‌بندی با اسلاگ (رایز کردن اکسپشن یا بازگرداندن None).
        در منیجر ما رایز می‌کند، اینجا هندل می‌کنیم تا سرویس اپلیکیشن بتونه None بگیره اگه خواست.
        """
        try:
            return ProductCategory.objects.get_by_slug(slug)
        except ProductCategoryNotFoundException:
            # در کد سرویس اپلیکیشن شما انتظار None دارد (if not category: return None)
            # پس اینجا اکسپشن را می‌گیریم و None برمی‌گردانیم
            return None

    def get_category_descendants_ids(self, slug: str) -> List[int]:
        """
        دریافت لیست شناسه‌های فرزندان برای فیلتر کردن محصولات.
        """
        try:
            category = ProductCategory.objects.get_by_slug(slug)
            return list(category.get_descendants(include_self=True).values_list('id', flat=True))
        except ProductCategoryNotFoundException:
            return []

    # ===== Write Operations ===== #
    @transaction.atomic
    def create_category(self, data: Dict[str, Any]) -> ProductCategory:
        """
        ایجاد یک دسته‌بندی جدید.
        """
        category = ProductCategory(**data)
        category.full_clean()
        category.save()
        return category

    @transaction.atomic
    def update_category(self, instance: ProductCategory, data: Dict[str, Any]) -> ProductCategory:
        """
        ویرایش دسته‌بندی.
        """
        for field, value in data.items():
            setattr(instance, field, value)
        instance.full_clean()
        instance.save()
        return instance

    def delete_category(self, instance: ProductCategory) -> None:
        """
        حذف یک دسته‌بندی.
        """
        instance.delete()

    # ===== Bulk Operations ===== #
    @transaction.atomic
    def bulk_toggle_status(self, ids: List[int], is_active: bool) -> int:
        return ProductCategory.objects.bulk_toggle_status(ids, is_active)

    @transaction.atomic
    def bulk_delete(self, ids: List[int]) -> tuple:
        return ProductCategory.objects.bulk_delete_categories(ids)

    def get_products_by_category_ids(self, category_ids: List[int]) -> QuerySet[Product]:
        """
        دریافت محصولات بر اساس لیستی از شناسه‌های دسته‌بندی.
        * اصلاح شده برای ساختار M2M *
        """
        return Product.objects.filter(
            is_active=True,
            categories__id__in=category_ids
        ).select_related(
            'pricing_config'
        ).distinct()
