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

    def upload_temp_file(self, uploaded_file, product_id: int, 
                         size_id: int = None, 
                         custom_width: float = None, 
                         custom_height: float = None) -> str:
        
        logger.info(f"Starting temp file upload for Product ID: {product_id}")

        # ===== دریافت ابعاد تصویر ===== #
        req_width, req_height = self._calculate_required_dimensions(
            product_id, size_id, custom_width, custom_height
        )
        
        # ===== اعتبارسنجی فنی فایل ===== #
        self._validate_file_technical_specs(uploaded_file, req_width, req_height)

        # ===== ذخیره فایل در مسیر موقت ===== #
        return self._save_file_to_temp(uploaded_file)

    def _calculate_required_dimensions(self, product_id: int, size_id: int = None, 
                                       custom_w: float = None, custom_h: float = None):
        """
        محاسبه ابعاد دقیق برای چاپ.
        این متد دقیقاً همان کاری را می‌کند که شما می‌خواهید:
        یا از سایزهای تعریف شده محصول می‌خواند یا ابعاد دلخواه را چک می‌کند.
        """
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            raise ValidationError("محصول یافت نشد.")

        # ===== گزینه‌های انتخابی برای ابعاد ===== #
        if size_id:
            try:
                prod_size = ProductSize.objects.select_related('size').get(
                    product=product, 
                    size_id=size_id
                )
                return prod_size.size.width, prod_size.size.height
            except ProductSize.DoesNotExist:
                raise ValidationError("سایز انتخاب شده برای این محصول معتبر نیست.")
        # ===== سایز دلخواه ===== #
        elif custom_w and custom_h:
            if not product.accepts_custom_dimensions:
                raise ValidationError("این محصول قابلیت سفارش با ابعاد دلخواه را ندارد.")
            
            return float(custom_w), float(custom_h)

        else:
            raise ValidationError("ابعاد محصول مشخص نشده است (نه سایز، نه ابعاد دلخواه).")

        
    def _validate_file_technical_specs(self, file, width, height):
        """
        بررسی‌های تخصصی چاپ: ابعاد، رنگ، کیفیت.
        """
        try:
            # ===== اعتبارسنجی ابعاد ===== #
            file.seek(0)
            validate_image_dimensions(file, width, height)
            # ===== اعتبارسنجی رنگ ===== #
            file.seek(0)
            validate_image_cmyk(file)
            # ===== اعتبارسنجی کیفیت ===== #
            file.seek(0)
            validate_image_dpi(file)
            
        except Exception as e:
            logger.warning(f"File validation failed: {e}")
            raise ValidationError(f"خطای فایل: {e}")

    def _save_file_to_temp(self, file) -> str:
        """
        ذخیره فیزیکی فایل با نام یونیک.
        """
        try:
            # ===== ساخت مسیر ذخیره سازی و نام فایل ===== #
            file.seek(0)
            ext = os.path.splitext(file.name)[1].lower()
            filename = f"{uuid.uuid4()}{ext}"
            
            # ===== مسیر ذخیره سازی ===== #
            save_path = os.path.join('uploads', 'temp', filename)
            default_storage.save(save_path, file)
            
            logger.info(f"Temp file saved: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Temp file save error: {e}")
            raise ValidationError("خطا در ذخیره‌سازی فایل موقت.")

    # def upload_temp_file(self, uploaded_file, product_id: int, 
    #     size_id: int = None, 
    #     custom_width: float = None, 
    #     custom_height: float = None) -> str:
    #     """
    #     اجرای پایپ‌لاین اعتبارسنجی و ذخیره فایل.

    #     Raises:
    #         ValidationError: در صورت عدم رعایت استانداردهای چاپ.
    #     """
    #     logger.info(f"Starting temp file upload for Product ID: {product_id}")
        
    #     try:
    #         # ===== یافتن ابعاد مورد نیاز ===== #
    #         req_width, req_height = self._get_required_dimensions(
    #             product_id, size_id, custom_width, custom_height
    #         )
            
    #         # ===== بررسی ابعاد فایل ===== #
    #         try:
    #             uploaded_file.seek(0)
    #             validate_image_dimensions(uploaded_file, req_width, req_height)
    #             logger.debug("Dimension validation passed.")
    #         except Exception as e:
    #             logger.warning(f"Dimension validation failed: {e}")
    #             raise ValidationError(f"خطای ابعاد: {e}")
            
    #         # ===== بررسی CMYK فایل ===== #
    #         try:
    #             uploaded_file.seek(0)
    #             validate_image_cmyk(uploaded_file)
    #             logger.debug("CMYK validation passed.")
    #         except Exception as e:
    #             logger.warning(f"CMYK validation failed: {e}")
    #             raise ValidationError(f"خطای مد رنگی: {e}")
            
    #         # ===== بررسی DPI فایل ===== #
    #         try:
    #             uploaded_file.seek(0)
    #             validate_image_dpi(uploaded_file)
    #             logger.debug("DPI validation passed.")
    #         except Exception as e:
    #             logger.warning(f"DPI validation failed: {e}")
    #             raise ValidationError(f"خطای کیفیت فایل: {e}")
            
    #         # ===== ذخیره سازی فایل ===== #
    #         try:
    #             uploaded_file.seek(0)
    #             original_extension = os.path.splitext(uploaded_file.name)[1]
    #             temp_filename = f"{uuid.uuid4()}{original_extension}"
    #             temp_path = os.path.join("uploads", "temp", temp_filename)
                
    #             default_storage.save(temp_path, uploaded_file)
                
    #             logger.info(f"File uploaded successfully: {temp_filename}")
    #             return temp_filename
            
    #         except Exception as e:
    #             logger.error(f"File save error: {str(e)}")
    #             raise ValidationError(f"خطا در ذخیره‌سازی فایل: {str(e)}")
                
    #     except ValidationError as e:
    #         raise e
    #     except Exception as e:
    #         logger.exception("Unexpected error in upload_temp_file")
    #         raise ValidationError("خطای سیستمی در آپلود فایل.")
