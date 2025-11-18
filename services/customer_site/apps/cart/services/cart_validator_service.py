from typing import Dict, Any

from rest_framework.exceptions import ValidationError

from core.models import (
    Product,
    ProductQuantity,
    ProductMaterial,
    ProductSize,
    ProductOption,
)
from core.common.product import ProductRepository

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
        
        # ===== دریافت ویژگی های محصول ===== #
        quantity_id = selections.get("quantity_id")
        material_id = selections.get("material_id")
        size_id = selections.get("size_id")
        options_ids = selections.get("options_ids", [])
        
        # ===== اعتبارسنجی وجود تیراژ برای محصول ===== #
        try:
            quantity_obj = product.product_quantity.get(id=quantity_id)
            material_obj = product.product_material.get(id=material_id)
            
            size_obj = None
            if size_id:
                size_obj = product.product_size.get(id=size_id)
                
            options_obj = list(product.product_option_product.filter(id__in=options_ids))
            if len(options_obj) != len(options_ids):
                raise ValidationError("یک یا چند گزینه انتخاب نشده است یا نامعتبر است.")
            
        except (
            ProductMaterial.DoesNotExist,
            ProductSize.DoesNotExist,
            ProductQuantity.DoesNotExist,
        ) as e:
            raise ValidationError(f"یکی از ویژگی های انتخاب شده برای محصول نامعتبر است: {str(e)}")
        
        # ===== بازگرداندن آبجکت های معتبر ===== #
        return {
            "product" : product,
            "quantity_obj" : quantity_obj,
            "material_obj" : material_obj,
            "size_obj" : size_obj,
            "options_obj" : options_obj,
            "custom_dimensions" : selections.get('custom_dimensions'),
        }
    
    