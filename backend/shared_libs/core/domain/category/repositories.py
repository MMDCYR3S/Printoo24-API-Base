from typing import Optional

from django.db.models import QuerySet

from core.models import ProductCategory
from ...utils.base_repository import BaseRepository
from .exceptions import ProductCategoryNotFoundException

# ===== Product Category Repository ===== #
class ProductCategoryRepository(BaseRepository[ProductCategory]):
    
    """
    ریپازیتوری اختصاصی برای دسته‌بندی‌ها.
    با توجه به استفاده از MPTT، کوئری‌ها باید خاص باشند.
    """
    def __init__(self):
        super().__init__(ProductCategory)

    def get_all_active_categories(self) -> QuerySet[ProductCategory]:
        """
        دریافت تمام دسته‌بندی‌ها.
        نکته کلیدی: MPTT متد get_cached_trees دارد که در پایتون درخت را می‌سازد،
        اما ما اینجا فقط کوئری‌ست خام و مرتب شده را می‌خواهیم.
        """
        return self.model.objects.all().order_by('tree_id', 'lft')

    def get_category_by_slug(self, slug: str) -> Optional[ProductCategory]:
        try:
            return self.model.objects.get(slug=slug)
        except self.model.DoesNotExist:
            raise ProductCategoryNotFoundException(f"دسته‌بندی با اسلاگ '{slug}' یافت نشد.")
            
    def get_descendants(self, category: ProductCategory) -> QuerySet[ProductCategory]:
        """
        دریافت تمام زیرمجموعه‌های یک دسته‌بندی (برای فیلترینگ محصولات لازم می‌شود).
        """
        return category.get_descendants(include_self=True)