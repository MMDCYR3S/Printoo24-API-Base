from typing import Dict, Any, List
from django.db import transaction
from django.db.models import QuerySet

from ..models import ProductCategory
from ..exceptions import ProductCategoryNotFoundException

# ========== CATEGORY SERVICE ========== #
class ProductCategoryService:
    """
    سرویس دامنه دسته‌بندی محصولات
    """
    
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

    def get_category_descendants_ids(self, slug: str) -> List[int]:
        """
        این متد برای سرویس "لیست محصولات" حیاتی است.
        وقتی کاربر روی "لوازم تحریر" کلیک می‌کند، باید محصولات "خودکار" (فرزند) هم بیاید.
        """
        category = ProductCategory.objects.get_by_slug(slug)
        
        # ===== بازگرداندن لیست شناسه‌های فرزندان ===== #
        return list(category.get_descendants(include_self=True).values_list('id', flat=True))
    
    # ===== ایجاد دسته‌بندی جدید ===== #
    @transaction.atomic
    def create_category(self, data: Dict[str, Any]) -> ProductCategory:
        """
        ایجاد یک دسته‌بندی جدید.
        """
        category = ProductCategory(**data)
        category.full_clean()
        category.save()
        return category

    # ===== ویرایش دسته‌بندی ===== #
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

    # ===== حذف تکی ===== #
    def delete_category(self, instance: ProductCategory) -> None:
        """
        حذف یک دسته‌بندی.
        نکته: چون MPTT است، حذف والد باعث حذف فرزندان می‌شود (Cascade).
        """
        instance.delete()

    # ===== عملیات دسته‌جمعی ===== #
    @transaction.atomic
    def bulk_toggle_status(self, ids: List[int], is_active: bool) -> int:
        return ProductCategory.objects.bulk_toggle_status(ids, is_active)

    @transaction.atomic
    def bulk_delete(self, ids: List[int]) -> tuple:
        return ProductCategory.objects.bulk_delete_categories(ids)
