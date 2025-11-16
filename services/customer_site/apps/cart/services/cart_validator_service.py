from typing import Dict, Any

from rest_framework.exceptions import ValidationError

from shared_libs.core.core.models import Product
from shared_libs.core.core.common.product import ProductRepository

# ======= Cart Data Validator ======= #
class CartDataValidator:
    """
    مسئول اعتبارسنجی داده‌های خام ورودی برای افزودن محصول به سبد خرید.
    این کلاس تضمین می‌کند که محصول و گزینه‌های انتخابی معتبر هستند.
    """
    
    def __init__(self):
        self._repository = ProductRepository()
        
    def validate(self, product_slug: str, selections: Dict[str, Any]) -> Product:
        """
        داده های مربوط به محصول رو بررسی می کند و در صورت موفقیت، اطلاعات
        مربوط به محصول رو باز می گرداند و در صورت ناموفقیت، یک خطا را برمی گرداند.
        هر انتخابی که کاربر در مورد محصول کرده است، ارزیابی می شود. مثلاً اگر سایز دلخواه 
        را انتخاب کرده و آن را خالی گذاشته است، خطا دهد یا اگر یکی از ویژگی های مورد
        نیاز رو انتخاب نکرده است، خطا دهد.
        """
        
        # ===== بررسی وجود محصول ===== #
        product = self._repository.get_product_detail_by_slug(slug=product_slug)
        if not product:
            raise ValidationError("محصول مورد نظر یافت نشد.")
        
        return product
    
    