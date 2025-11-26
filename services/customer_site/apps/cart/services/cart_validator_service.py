import logging
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

# ===== تعریف لاگر اختصاصی برای سرویس اعتبارسنجی سبد خرید ===== #
logger = logging.getLogger('shop.services.cart_validator')

class CartDataValidator:
    """
    مسئول اعتبارسنجی داده‌های خام ورودی برای افزودن محصول به سبد خرید.
    
    این کلاس به عنوان یک گارد امنیتی عمل می‌کند و تضمین می‌کند که:
    1. محصول مورد نظر وجود داشته باشد.
    2. تمام ویژگی‌های انتخابی (جنس، سایز، تیراژ و...) معتبر و متعلق به آن محصول باشند.
    3. داده‌های ضروری از قلم نیفتاده باشند.
    """
    
    def __init__(self):
        # ===== تزریق وابستگی مخزن محصول ===== #
        self._repository = ProductRepository()
        
    def validate(self, product_slug: str, selections: Dict[str, Any]) -> Dict[str, Any]:
        """
        اجرای فرآیند اعتبارسنجی داده‌های محصول و انتخاب‌های کاربر.

        Args:
            product_slug (str): اسلاگ محصول برای جستجو.
            selections (Dict[str, Any]): دیکشنری حاوی شناسه‌های انتخابی کاربر (quantity_id, material_id, ...).

        Returns:
            Dict[str, Any]: دیکشنری شامل آبجکت‌های معتبر شده دیتابیس (Product, Size, Material و...).

        Raises:
            ValidationError: در صورت عدم وجود محصول یا نامعتبر بودن هر یک از ویژگی‌ها.
        """
        logger.info(f"Starting validation for Product Slug: {product_slug}")
        logger.debug(f"Selections received: {selections}")
        
        # ===== بررسی وجود محصول ===== #
        product = self._repository.get_product_detail_by_slug(slug=product_slug)
        if not product:
            logger.warning(f"Product not found with slug: {product_slug}")
            raise ValidationError("محصول مورد نظر یافت نشد.")
        
        # ===== استخراج شناسه‌ها از ورودی ===== #
        quantity_id = selections.get("quantity_id")
        material_id = selections.get("material_id")
        size_id = selections.get("size_id")
        options_ids = selections.get("options_ids", [])
        
        # ===== شروع بلوک اعتبارسنجی ویژگی‌ها ===== #
        try:
            # ===== اعتبارسنجی تیراژ و متریال (اجباری) ===== #
            quantity_obj = product.product_quantity.get(id=quantity_id)
            material_obj = product.product_material.get(id=material_id)
            
            # ===== اعتبارسنجی سایز (اختیاری) ===== #
            size_obj = None
            if size_id:
                size_obj = product.product_size.get(id=size_id)
            
            # ===== اعتبارسنجی آپشن‌های اضافی ===== #
            # نکته: فیلتر کردن بر اساس محصول برای اطمینان از اینکه آپشن متعلق به همین محصول است
            options_obj = list(product.product_option_product.filter(id__in=options_ids))
            
            # چک کردن اینکه آیا تمام آپشن‌های درخواستی پیدا شدند یا خیر
            if len(options_obj) != len(options_ids):
                logger.warning(
                    f"Option mismatch for Product: {product.name}. "
                    f"Requested: {len(options_ids)}, Found: {len(options_obj)}"
                )
                raise ValidationError("یک یا چند گزینه انتخاب شده نامعتبر است یا به این محصول تعلق ندارد.")
            
            logger.debug("All product attributes validated successfully.")

            # ===== بازگرداندن آبجکت‌های معتبر ===== #
            return {
                "product": product,
                "quantity_obj": quantity_obj,
                "material_obj": material_obj,
                "size_obj": size_obj,
                "options_obj": options_obj,
                "custom_dimensions": selections.get('custom_dimensions'),
            }
            
        except (
            ProductMaterial.DoesNotExist,
            ProductSize.DoesNotExist,
            ProductQuantity.DoesNotExist,
        ) as e:
            logger.error(f"Validation attribute error for Product {product_slug}: {str(e)}")
            raise ValidationError(f"یکی از ویژگی‌های انتخاب شده برای محصول نامعتبر است.")
            
        except Exception as e:
            if isinstance(e, ValidationError):
                raise e
            logger.exception(f"Unexpected validation error for Product {product_slug}")
            raise ValidationError("خطای سیستمی در اعتبارسنجی محصول.")
