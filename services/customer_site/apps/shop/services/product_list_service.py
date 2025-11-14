# customer_site/shop/services.py

from typing import Dict, Any, List, Optional
from collections import defaultdict
from django.db.models import QuerySet

from core.common.product import ProductService
from core.models import Product, ProductOption

# ======= Shop Product List Service ======= #
class ShopProductListService:
    """
    سرویس لایه کاربردی برای مورد استفاده "نمایش لیست محصولات".
    این سرویس مسئول دریافت کوئری‌ست اولیه و آماده‌سازی آن برای فیلترینگ و نمایش است.
    """
    def __init__(self, product_service: ProductService):
        self._product_service = product_service

    def get_base_queryset(self) -> QuerySet[Product]:
        """
        کوئری‌ست پایه و بهینه‌سازی شده برای لیست محصولات را برمی‌گرداند.
        این کوئری‌ست سپس در لایه View برای فیلترینگ استفاده خواهد شد.
        """
        return self._product_service.get_all_active_products()
