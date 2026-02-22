from typing import Dict, Any
from decimal import Decimal

from django.core.exceptions import ValidationError
from core.product.models import Product
from core.product.services.calculator import ProductPricingDomainService
from core.product.exceptions import InvalidProductDataException

class CartProcessor:
    """
    مغز متفکر سبد خرید (متصل به موتور جدید فیلدساز و فرمول‌ساز).
    مسئولیت‌ها:
    ۱. دریافت ورودی خام کاربر (تمام انتخاب‌ها شامل تیراژ داینامیک).
    ۲. ارسال به سرویس دامنه برای محاسبه قیمت و استخراج خلاصه انتخاب‌ها.
    ۳. آماده‌سازی خروجی برای ذخیره در مدل CartItem.
    """
    def __init__(self, product: Product, selections: Dict[str, Any]):
        self.product = product
        self.raw_selections = selections
        
        # ===== مقادیری که باید امال شوند ===== #
        self.result_price = Decimal('0.0')
        self.result_item_data = {}
        self.result_name = self.product.name
        self.result_description = ""

    def process(self):
        """
        اجرای فرایند پردازش و محاسبه قیمت.
        """
        try:
            # ===== محاسبه خودکار براساس فرمول محصول ===== # 
            final_price, configuration_summary = ProductPricingDomainService.calculate_final_price(
                product_id=self.product.id,
                user_selections=self.raw_selections
            )
            
            # ===== تنظیم قیمت نهایی ===== #
            self.result_price = final_price
            self.result_item_data = configuration_summary
            
            # ===== ساخت یک رشته توضیحات ===== #
            desc_parts = [f"{key}: {val}" for key, val in configuration_summary.items()]
            self.result_description = " | ".join(desc_parts)

        except InvalidProductDataException as e:
            raise ValidationError(str(e))
        except Exception as e:
            raise ValidationError(f"خطای سیستمی در محاسبه قیمت سبد خرید: {str(e)}")

        return self
