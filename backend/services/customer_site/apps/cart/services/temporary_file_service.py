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

logger = logging.getLogger('cart.services.temp_file')

class TemporaryFileService:
    """
    سرویس مدیریت آپلود و اعتبارسنجی فایل‌های موقت (نسخه هماهنگ با ProductPricingConfig).
    """

    def upload_temp_file(self, uploaded_file, product_id: int, 
                         size_id: int = None, 
                         custom_width: float = None, 
                         custom_height: float = None) -> str:
        
        logger.info(f"Starting temp file upload for Product ID: {product_id}")

        # 1. محاسبه ابعاد مورد نیاز بر اساس کانفیگ جدید
        req_width, req_height = self._calculate_required_dimensions(
            product_id, size_id, custom_width, custom_height
        )
        
        # 2. اعتبارسنجی فنی فایل
        self._validate_file_technical_specs(uploaded_file, req_width, req_height)

        # 3. ذخیره فایل
        return self._save_file_to_temp(uploaded_file)

    def _calculate_required_dimensions(self, product_id: int, size_id: int = None, 
                                       custom_w: float = None, custom_h: float = None):
        """
        محاسبه ابعاد دقیق با توجه به مدل جدید ProductPricingConfig.
        """
        try:
            # دریافت محصول به همراه کانفیگ قیمت‌گذاری
            product = Product.objects.select_related('pricing_config').get(pk=product_id)
        except Product.DoesNotExist:
            raise ValidationError("محصول یافت نشد.")

        # دسترسی به کانفیگ
        config = getattr(product, 'pricing_config', None)
        if not config:
            raise ValidationError("تنظیمات محصول (Pricing Config) یافت نشد.")

        # ===== سناریوی ۱: انتخاب سایز استاندارد ===== #
        if size_id:
            try:
                prod_size = ProductSize.objects.select_related('size').get(
                    product=product, 
                    id=size_id # دقت کنید که ID جدول واسط ProductSize ملاک است
                )
                return prod_size.size.width, prod_size.size.height
            except ProductSize.DoesNotExist:
                raise ValidationError("سایز انتخاب شده برای این محصول معتبر نیست.")

        # ===== سناریوی ۲: ابعاد دلخواه ===== #
        elif custom_w and custom_h:
            # چک کردن فیلد از داخل Config
            if not config.accepts_custom_dimensions:
                raise ValidationError("این محصول قابلیت سفارش با ابعاد دلخواه را ندارد.")
            
            width = float(custom_w)
            height = float(custom_h)

            # چک کردن محدودیت‌های عرض دستگاه از داخل Config
            if config.min_width and width < config.min_width:
                 raise ValidationError(f"حداقل عرض قابل چاپ {config.min_width} سانتیمتر است.")
            if config.max_width and width > config.max_width:
                 raise ValidationError(f"حداکثر عرض قابل چاپ {config.max_width} سانتیمتر است.")

            return width, height

        else:
            raise ValidationError("ابعاد محصول مشخص نشده است (نه سایز، نه ابعاد دلخواه).")

    def _validate_file_technical_specs(self, file, width, height):
        """بررسی‌های تخصصی چاپ"""
        try:
            # ریست کردن پوینتر فایل قبل از هر خواندن حیاتی است
            file.seek(0)
            validate_image_dimensions(file, width, height)
            
            file.seek(0)
            validate_image_cmyk(file)
            
            file.seek(0)
            validate_image_dpi(file)
            
        except Exception as e:
            logger.warning(f"File validation failed: {e}")
            # بازگرداندن متن خطای اصلی برای نمایش به کاربر
            raise ValidationError(str(e))

    def _save_file_to_temp(self, file) -> str:
        """ذخیره فیزیکی فایل"""
        try:
            file.seek(0)
            ext = os.path.splitext(file.name)[1].lower()
            filename = f"{uuid.uuid4()}{ext}"
            
            save_path = os.path.join('uploads', 'temp', filename)
            default_storage.save(save_path, file)
            
            logger.info(f"Temp file saved: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Temp file save error: {e}")
            raise ValidationError("خطا در ذخیره‌سازی فایل موقت.")
