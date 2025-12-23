import logging
from typing import Dict, Any, List, Optional
from collections import defaultdict
from django.db.models import QuerySet

from core.product.services import ProductService
from core.models import ProductOption

# ====== Logger Configuration ====== #
logger = logging.getLogger('shop.services.product_detail')


# ======= Shop Product Detail Service ======= #
class ShopProductDetailService:
    """
    سرویس لایه کاربردی برای مورد استفاده "نمایش جزئیات یک محصول"
    """
    def __init__(self):
        self._product_service = ProductService()
        logger.debug("ShopProductDetailService initialized")
        
    def get_product_detail_for_display(self, slug: str) -> Optional[object]:
        """
        دریافت آبجکت محصول با تمام ریلیشن‌های لود شده (Eager Loading).
        خروجی: آبجکت Product یا None.
        """
        try:
            
            data = self._product_service.get_product_detail_by_slug(slug)
            print(data)
            
            if not data or 'product' not in data:
                return None
                
            return data['product']

        except Exception as e:
            logger.error(f"Error fetching product: {e}")
            return None
