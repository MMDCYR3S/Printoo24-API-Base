from typing import Dict, Any, List

from django.db.models import QuerySet
from django.db import transaction

from core.models import ProductCategory
from .repositories import ProductCategoryRepository
from .exceptions import ProductCategoryNotFoundException

# ===== Product Category Domain Service ===== #
class ProductCategoryDomainService:
    def __init__(self):
        self._repo = ProductCategoryRepository()
    
    # ===== دریافت لیست دسته‌بندی‌ها به صورت درختی ===== #
    def get_category_tree_queryset(self) -> QuerySet[ProductCategory]:
        """
        فقط کوئری‌ست را برمی‌گرداند. تبدیل به درخت وظیفه لایه نمایش است.
        """
        return self._repo.get_all_active_categories()

    # ===== دریافت شاخص‌های فرزندان ===== #
    def get_category_descendants_ids(self, slug: str) -> List[int]:
        """
        این متد برای سرویس "لیست محصولات" حیاتی است.
        وقتی کاربر روی "لوازم تحریر" کلیک می‌کند، باید محصولات "خودکار" (فرزند) هم بیاید.
        """
        category = self._repo.get_category_by_slug(slug)
        if not category:
            raise ProductCategoryNotFoundException(f"دسته‌بندی با اسلاگ '{slug}' یافت نشد.")
        
        # ===== بازگرداندن لیست شناسه‌های فرزندان ===== #
        return list(self._repo.get_descendants(category).values_list('id', flat=True))
    
    # ===== ایجاد دسته‌بندی جدید ===== #
    @transaction.atomic
    def create_category(self, data: Dict[str, Any]) -> ProductCategory:
        """
        ایجاد یک دسته‌بندی جدید.
        اینجا می‌توانیم لاجیک‌های خاص مثل چک کردن یونیک بودن نام
        در یک سطح خاص را اضافه کنیم.
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
        نکته: برای آپدیت فیلدها از setattr استفاده می‌کنیم تا داینامیک باشد.
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

    # ===== عملیات دسته‌جمعی: تغییر وضعیت ===== #
    @transaction.atomic
    def bulk_toggle_status(self, ids: List[int], is_active: bool) -> int:
        """
        تغییر وضعیت فعال/غیرفعال برای تعدادی دسته‌بندی.
        خروجی: تعداد رکوردهای آپدیت شده.
        """
        return self._repo.model.objects.filter(id__in=ids).update(is_active=is_active)

    # ===== عملیات دسته‌جمعی: حذف ===== #
    @transaction.atomic
    def bulk_delete(self, ids: List[int]) -> tuple:
        """
        حذف گروهی.
        """
        return self._repo.model.objects.filter(id__in=ids).delete()