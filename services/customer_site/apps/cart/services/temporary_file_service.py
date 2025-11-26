import uuid
import os
import logging

from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from rest_framework.exceptions import ValidationError

from core.models import Product, ProductSize
from ..utils.validators import (
    validate_image_cmyk,
    validate_image_dpi,
    validate_image_dimensions,
)

# ===== تعریف لاگر اختصاصی برای سرویس فایل‌های موقت ===== #
logger = logging.getLogger('cart.services.temp_file')

# ======== Temporary File Service ======== #
class TemporaryFileService:
    """
    سرویس مدیریت آپلود و اعتبارسنجی فایل‌های موقت.
    
    این سرویس پیش از افزودن محصول به سبد خرید اجرا می‌شود و وظیفه دارد:
    1. ابعاد دقیق مورد نیاز (بر اساس سایز یا ابعاد دلخواه) را محاسبه کند.
    2. فایل آپلود شده را از نظر فنی (DPI, CMYK, Dimensions) اعتبارسنجی کند.
    3. فایل را در پوشه موقت ذخیره کرده و نام آن را برگرداند.
    """

    def _get_required_dimensions(self, product_id: int, size_id: int = None, 
                                 custom_w: float = None, custom_h: float = None):
        """
        محاسبه ابعاد مورد نیاز بر اساس ورودی‌ها.
        
        Returns:
            tuple: (width, height)
        """
        logger.debug(f"Calculating dimensions for Product: {product_id}, Size: {size_id}, Custom: {custom_w}x{custom_h}")
        
        product = get_object_or_404(Product, pk=product_id)
        
        # ===== اگر سایز، پیش فرض محصول بود ===== #
        if size_id:
            product_size = ProductSize.objects.filter(product=product, size_id=size_id).first()
            if not product_size:
                logger.warning(f"Invalid Size ID {size_id} for Product {product_id}")
                raise ValidationError("سایز انتخاب شده برای این محصول معتبر نیست.")
            return product_size.size.width, product_size.size.height
        
        # ===== اگر سایز، ابعاد دلخواه بود ===== #
        elif custom_w and custom_h:
            if not product.accepts_custom_dimensions:
                logger.warning(f"Product {product_id} does not accept custom dimensions.")
                raise ValidationError("این محصول قابلیت ابعاد دلخواه را ندارد.")
            return custom_w, custom_h
        
        else:
            raise ValidationError("مشخصات سایز به درستی ارسال نشده است.")

    def upload_temp_file(self, uploaded_file, product_id: int, 
        size_id: int = None, 
        custom_width: float = None, 
        custom_height: float = None) -> str:
        """
        اجرای پایپ‌لاین اعتبارسنجی و ذخیره فایل.

        Raises:
            ValidationError: در صورت عدم رعایت استانداردهای چاپ.
        """
        logger.info(f"Starting temp file upload for Product ID: {product_id}")
        
        try:
            # ===== یافتن ابعاد مورد نیاز ===== #
            req_width, req_height = self._get_required_dimensions(
                product_id, size_id, custom_width, custom_height
            )
            
            # ===== بررسی ابعاد فایل ===== #
            try:
                uploaded_file.seek(0)
                validate_image_dimensions(uploaded_file, req_width, req_height)
                logger.debug("Dimension validation passed.")
            except Exception as e:
                logger.warning(f"Dimension validation failed: {e}")
                raise ValidationError(f"خطای ابعاد: {e}")
            
            # ===== بررسی CMYK فایل ===== #
            try:
                uploaded_file.seek(0)
                validate_image_cmyk(uploaded_file)
                logger.debug("CMYK validation passed.")
            except Exception as e:
                logger.warning(f"CMYK validation failed: {e}")
                raise ValidationError(f"خطای مد رنگی: {e}")
            
            # ===== بررسی DPI فایل ===== #
            try:
                uploaded_file.seek(0)
                validate_image_dpi(uploaded_file)
                logger.debug("DPI validation passed.")
            except Exception as e:
                logger.warning(f"DPI validation failed: {e}")
                raise ValidationError(f"خطای کیفیت فایل: {e}")
            
            # ===== ذخیره سازی فایل ===== #
            try:
                uploaded_file.seek(0)
                original_extension = os.path.splitext(uploaded_file.name)[1]
                temp_filename = f"{uuid.uuid4()}{original_extension}"
                temp_path = os.path.join("uploads", "temp", temp_filename)
                
                default_storage.save(temp_path, uploaded_file)
                
                logger.info(f"File uploaded successfully: {temp_filename}")
                return temp_filename
            
            except Exception as e:
                logger.error(f"File save error: {str(e)}")
                raise ValidationError(f"خطا در ذخیره‌سازی فایل: {str(e)}")
                
        except ValidationError as e:
            raise e
        except Exception as e:
            logger.exception("Unexpected error in upload_temp_file")
            raise ValidationError("خطای سیستمی در آپلود فایل.")
