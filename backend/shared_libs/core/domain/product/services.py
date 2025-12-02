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
        
        # ===== تبدیل ساختار آپشن‌ها به فرمت استاندارد API ===== #
        structured_options = []
        
        # ===== مرتب‌سازی گزینه‌ها ===== #
        for prod_opt in product.options.all():
            option_data = {
                    "id": prod_opt.id,                # ID کانفیگ (برای ارسال در سبد خرید)
                    "name": prod_opt.option.name,     # نام سیستمی (paper_type)
                    "label": prod_opt.option.label,   # نام نمایشی (جنس کاغذ)
                    "type": prod_opt.option.input_type, # نوع اینپوت (select, radio, ...)
                    "is_required": prod_opt.is_required,
                    "description": prod_opt.option.description,
                    "has_pricing": prod_opt.has_pricing, # آیا کلا قیمت دارد؟
                    "choices": []
                }
            for choice in prod_opt.choices.all():
                option_data["choices"].append({
                    "id": choice.id,        # ID ولیو (برای ارسال در سبد خرید)
                    "label": choice.label,
                    "value": choice.value,
                    "price_impact": choice.price_impact, # جهت نمایش به کاربر (+5000)
                    "is_default": choice.is_default,
                    "description": f"هر {choice.quantity_step} عدد" if choice.quantity_step > 1 else ""
                })
            structured_options.append(option_data)
        
        # ===== بازگشت اطلاعات محصول ===== #
        return {
            "product": product,
            "structured_options": structured_options
        }
            