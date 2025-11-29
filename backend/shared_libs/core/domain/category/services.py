from typing import Optional, List

from django.db.models import QuerySet

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
        return list(category.get_descendants(include_self=True).values_list('id', flat=True))