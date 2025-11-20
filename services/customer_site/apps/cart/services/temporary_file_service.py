import uuid
import os

from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from rest_framework.exceptions import ValidationError

from core.models import Product, Size, ProductSize
from ..utils.validators import (
    validate_image_cmyk,
    validate_image_dpi,
    validate_image_dimensions,
)

# ======== Temporary File Service ======== #
class TemporaryFileService:
    """
    سرویس مدیریت آپلود فایل‌های موقت با قابلیت بررسی ابعاد محصول.
    """

    def _get_required_dimensions(self, product_id: int, size_id: int = None, 
                                 custom_w: float = None, custom_h: float = None):
        """
        محاسبه ابعاد مورد نیاز بر اساس ورودی‌ها
        خروجی: (width, height)
        """
        product = get_object_or_404(Product, pk=product_id)
        
        # ===== اگر سایز، پیش فرض محصول بود ===== #
        if size_id:
            product_size = ProductSize.objects.filter(product=product, size_id=size_id).first()
            if not product_size:
                raise ValidationError("سایز انتخاب شده برای این محصول معتبر نیست.")
            return product_size.size.width, product_size.size.height
        
        # ===== اگر سایز، ابعاد دلخواه بود ===== #
        elif custom_w and custom_h:
            if not product.accepts_custom_dimensions:
                raise ValidationError("این محصول قابلیت ابعاد دلخواه را ندارد.")
            return custom_w, custom_h
        
        else:
            raise ValidationError("مشخصات سایز به درستی ارسال نشده است.")
    def upload_temp_file( self, uploaded_file, product_id: int, 
        size_id: int = None, 
        custom_width: float = None, 
        custom_height: float = None) -> str:
        """
        فایل را اعتبارسنجی (CMYK, DPI, Dimensions) و ذخیره می‌کند.
        """
        
        # ===== یافتن ابعاد مورد نیاز ===== #
        req_width, req_height = self._get_required_dimensions(
            product_id, size_id, custom_width, custom_height
        )
        # ===== بررسی سایز فایل ===== #
        try:
            uploaded_file.seek(0)
            validate_image_dimensions(uploaded_file, req_width, req_height)
        except Exception as e:
            raise ValidationError(f"خطای ابعاد: {e}")
        
        # ===== بررسی CMYK فایل ===== #
        try:
            uploaded_file.seek(0)
            validate_image_cmyk(uploaded_file)
        except Exception as e:
            raise ValidationError(f"خطای مد رنگی: {e}")
        
        # ===== بررسی DPI فایل ===== #
        try:
            uploaded_file.seek(0)
            validate_image_dpi(uploaded_file)
        except Exception as e:
            raise ValidationError(f"خطای کیفیت فایل: {e}")
        
        # ===== ذخیره سازی فایل ===== #
        try:
            uploaded_file.seek(0)
            original_extension = os.path.splitext(uploaded_file.name)[1]
            temp_filename = f"{uuid.uuid4()}{original_extension}"
            temp_path = os.path.join("uploads", "temp", temp_filename)
            
            default_storage.save(temp_path, uploaded_file)
            return temp_filename
        # ===== در صورت ذخیره نکردن فایل، خطا رخ بده ===== #
        except Exception as e:
            raise ValidationError(f"خطا در ذخیره‌سازی فایل: {str(e)}")
        