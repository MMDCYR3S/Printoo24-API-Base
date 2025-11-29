import logging
from typing import Dict, Any, List, Optional
from collections import defaultdict
from django.db.models import QuerySet

from core.domain.product import ProductDomainService
from core.models import Product, ProductOption

# ====== Logger Configuration ====== #
logger = logging.getLogger('shop.services.product_list')


# ======= Shop Product List Service ======= #
class ShopProductListService:
    """
    سرویس لایه کاربردی برای مورد استفاده "نمایش لیست محصولات".
    این سرویس مسئول دریافت کوئری‌ست اولیه و آماده‌سازی آن برای فیلترینگ و نمایش است.
    """
    def __init__(self):
        self._product_service = ProductDomainService()
        logger.debug("ShopProductListService initialized")

    def get_base_queryset(self) -> QuerySet[Product]:
        """
        کوئری‌ست پایه و بهینه‌سازی شده برای لیست محصولات را برمی‌گرداند.
        این کوئری‌ست سپس در لایه View برای فیلترینگ استفاده خواهد شد.
        """
        logger.info("Fetching base queryset for product list")
        
        try:
            queryset = self._product_service.get_all_active_products()
            product_count = queryset.count()
            
            logger.info(f"Base queryset retrieved successfully - Total active products: {product_count}")
            logger.debug(f"Queryset details: {queryset.query}")
            
            return queryset
            
        except Exception as e:
            logger.error(
                f"Error fetching base queryset for product list: {str(e)}",
                exc_info=True
            )
            raise