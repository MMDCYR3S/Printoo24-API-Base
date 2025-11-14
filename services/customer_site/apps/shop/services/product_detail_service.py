from typing import Dict, Any, List, Optional
from collections import defaultdict
from django.db.models import QuerySet

from core.common.product.product_services import ProductService as CoreProductService
from core.models import Product, ProductOption

# ======= Shop Product Detail Service ======= #
class ShopProductDetailService:
    """
    سرویس لایه کاربردی برای مورد استفاده "نمایش جزئیات یک محصول"
    """
    def __init__(self):
        self.core_product_service = CoreProductService()
        
    def get_product_detail_for_display(self, slug: str) -> Optional[Dict[str, Any]]:
        """
        مورد استفاده: دریافت و آماده‌سازی جزئیات یک محصول برای نمایش در صفحه جزئیات.
        """
        # ===== دریافت جزئیات یک مصحول از سرویس ===== #
        product = self._product_service.get_product_detail_by_slug(slug)
        
        if not product:
            return None
            
        # ===== دریافت تمامی ویژگی های یک محصول منحصر به فرد به صورت بهینه ===== #
        quantities = list(product.productquantity_set.all())
        sizes = list(product.productsize_set.all())
        materials = list(product.productmaterial_set.all())
        options = list(product.productoption_set.all())

        # ===== گروه بندی ویژگی های منحصر به فرد محصول ===== #
        grouped_options = self._group_options_by_type(options)
        
        # ===== ایجاد دیکشنری ===== #
        product_details = {
            'product': product,
            'quantities': quantities,
            'sizes': sizes,
            'materials': materials,
            'options': grouped_options,
        }
        
        return product_details

    def _group_options_by_type(self, options: List[ProductOption]) -> Dict[str, List[ProductOption]]:
        """
        یک متد کمکی برای گروه‌بندی آپشن‌های محصول بر اساس نوع آن‌ها.
        این منطق متعلق به لایه نمایش است و به درستی در این سرویس قرار گرفته است.
        """
        grouped = defaultdict(list)
        for po in options:
            option_type_name = po.option_value.option.name
            grouped[option_type_name].append(po)
        return dict(grouped)
