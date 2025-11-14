from typing import Dict, Any, List, Optional
from collections import defaultdict

from .product_repo import ProductRepository
from core.models import Product, ProductOption

# ======== Product Service ======== #
from typing import List, Optional
from django.db.models import QuerySet

from .product_repo import ProductRepository
from core.models import Product

class ProductService:
    """
    سرویس هسته (Core Service) برای مدیریت منطق بنیادی محصولات.
    این سرویس به عنوان یک رابط تمیز برای ProductRepository عمل می‌کند.
    این لایه هیچ منطق خاصی برای اپلیکیشن‌ها (مانند نحوه نمایش) ندارد.
    """
    
    def __init__(self):
        self.repo = ProductRepository()

    def get_all_active_products(self) -> QuerySet[Product]:
        """
        دریافت لیستی از تمام محصولات فعال.
        مستقیماً متد ریپازیتوری را فراخوانی می‌کند.
        """
        return self.repo.get_all_products()

    def get_product_detail_by_slug(self, slug: str) -> Optional[Product]:
        """
        دریافت جزئیات کامل یک محصول (شامل تمام روابط prefetch شده).
        این متد آبجکت خام و بهینه‌سازی شده Product را برمی‌گرداند.
        """
        return self.repo.get_product_detail_by_slug(slug)