from typing import List, Optional
from collections import defaultdict

from django.db.models import QuerySet

from .exceptions import (
    ProductNotFoundException,
    ProductAlreadyExistsException,
    InvalidProductDataException
)
from .repositories import ProductRepository
from core.models import Product

# ======== Product Service ======== #
class ProductDomainService:
    """
    سرویس هسته (Core Service) برای مدیریت منطق بنیادی محصولات.
    این سرویس به عنوان یک رابط تمیز برای ProductRepository عمل می‌کند.
    این لایه هیچ منطق خاصی برای اپلیکیشن‌ها (مانند نحوه نمایش) ندارد.
    """
    
    def __init__(self):
        self._repo = ProductRepository()

    def get_all_active_products(self) -> QuerySet[Product]:
        """
        دریافت لیستی از تمام محصولات فعال.
        مستقیماً متد ریپازیتوری را فراخوانی می‌کند.
        """
        return self._repo.get_all_products()

    def get_product_detail_by_slug(self, slug: str) -> Optional[Product]:
        """
        دریافت جزئیات کامل یک محصول با استفاده از اسلاگ آن.
        این قسمت با استفاده از روابط پیچیده، تمامی ویژگی های محصول
        را با دقت بررسی کرده و با ساختار درختی درست، آن ها را برای
        نمایش به فرانت ارسال می کند.
        """
        product = self._repo.get_product_detail_by_slug(slug)
        if not product:
            raise ProductNotFoundException(f"Product with slug '{slug}' not found.")
        
        # ===== گروه‌بندی گزینه‌های محصول بر اساس نام گزینه ===== #
        grouped_options = defaultdict(list)
        
        # ===== مرتب‌سازی گزینه‌ها ===== #
        for prod_opt in product.product_option_product.all():
            option_name = prod_opt.option_value.option.name
            value_data = {
                "id": prod_opt.id,
                "value_id": prod_opt.option_value.id,
                "value": prod_opt.option_value.value,
                "price_impact": prod_opt.price_impact
            }
            grouped_options[option_name].append(value_data)
        
        # ===== بازگشت اطلاعات محصول ===== #
        return {
            "product": product,
            "grouped_options": dict(grouped_options)
        }
            