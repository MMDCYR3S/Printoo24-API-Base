import logging
from typing import List, Dict, Any
from mptt.utils import get_cached_trees

from rest_framework.reverse import reverse
from django.urls import NoReverseMatch

from core.domain.category import ProductCategoryDomainService
from core.models import ProductCategory

logger = logging.getLogger('shop.services.category')

# ====== Shop Category Service ======= #
class ShopCategoryService:
    """
    سرویس اپلیکیشن برای مدیریت نمایش دسته‌بندی‌ها و درختواره.
    """
    def __init__(self, request=None):
        self.request = request
        self._domain_service = ProductCategoryDomainService()
        
    # ===== = دریافت درختواره دسته‌بندی ====== #
    def get_category_tree_structure(self) -> List[Dict[str, Any]]:
        """
        تبدیل کوئری‌ست فلت به ساختار درختی تودرتو (Nested Dictionary).
        این متد برای منوهای بازشونده و سایدبار فیلترینگ عالی است.
        """
        logger.info("Building category tree with hyperlinks")
        
        # ===== دریافت کوئری‌ست دسته‌بندی‌ها ===== #
        categories = self._domain_service.get_category_tree_queryset()
        
        # ===== ساختار درختی ===== #
        root_nodes = get_cached_trees(categories)
        return [self._serialize_node(node) for node in root_nodes]
    
    # ===== تبدیل یک نود به دیکشنری =====
    def _serialize_node(self, node: ProductCategory) -> Dict[str, Any]:
        """
        تبدیل یک نود (و فرزندانش) به دیکشنری
        """
        
        children = [self._serialize_node(child) for child in node.get_children()]
        
        data = {
            "id": node.id,
            "name": node.name,
            "slug": node.slug,
            "has_children": len(children) > 0,
            "links": {
                "products_url" : self._generate_product_filter_url(node.slug),
            },
            "children": children,
        }
        return data
        
    def _generate_product_filter_url(self, slug: str) -> str:
        """
        تولید لینک فیلتر محصولات با اسلاگ دسته‌بندی
        """
        if not self.request:
            return None
        
        try:
            # ===== تولید لینک با استفاده از reverse ===== #
            base_url = reverse("api:v1:shop:list", request=self.request)
            # ===== تبدیل اسلاگ به لینک =====
            return f"{base_url}?category={slug}"
        
        except NoReverseMatch:
            logger.error(f"No reverse match found for category slug '{slug}'")
            
        except Exception as e:
            logger.error(f"Error generating product filter URL for category slug '{slug}': {str(e)}")
            return None