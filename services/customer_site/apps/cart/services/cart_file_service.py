import os
import shutil
import logging
from typing import Dict

from django.conf import settings
from django.core.files.base import ContentFile
from rest_framework.exceptions import ValidationError

from core.models import CartItem, CartItemUpload

# ===== تعریف لاگر اختصاصی برای سرویس فایل‌های سبد خرید ===== #
logger = logging.getLogger('cart.services.cart_file')

class FileFinalizeService:
    """
    سرویس مدیریت نهایی‌سازی فایل‌های آپلود شده موقت.
    
    این سرویس وظیفه دارد فایل‌هایی که کاربر به صورت موقت آپلود کرده است را
    بررسی کرده، آن‌ها را به مدل‌های نهایی (CartItemUpload) متصل کند
    و فایل‌های موقت را از سیستم فایل حذف نماید.
    
    وظایف اصلی:
    1. بررسی الزامی بودن فایل‌ها بر اساس محصول.
    2. انتقال فایل از پوشه temp به پوشه نهایی مدیا.
    3. ایجاد رکورد در دیتابیس برای فایل‌های نهایی.
    4. پاکسازی فایل‌های موقت پس از اتمام کار یا بروز خطا.
    """
    
    def finalize_files(self, temp_files_map: Dict[str, str], user_id: int) -> Dict[int, str]:
        """
        فایل‌ها را از temp به cart_uploads منتقل می‌کند و دیکشنری مسیرهای نسبی را برمی‌گرداند.
        
        Args:
            temp_files_map: {spec_id_str: temp_filename}
            
        Returns:
            {spec_id_int: relative_path_in_media}
        """
        final_paths = {}
        
        # ===== پردازش هر فایل موقت ===== #
        for spec_id_str, temp_name in temp_files_map.items():
            try:
                spec_id = int(spec_id_str)
                # ===== دریافت اطلاعات هر عکس ===== #
                temp_path = os.path.join(settings.MEDIA_ROOT, 'uploads', 'temp', temp_name)
                
                if not os.path.exists(temp_path):
                    logger.error(f"Temp file missing: {temp_path}")
                    raise ValidationError(f"فایل موقت {temp_name} یافت نشد (شاید منقضی شده است).")
                
                # ===== آماده‌سازی مسیر نهایی ===== #
                dest_rel_dir = f"cart_uploads/{user_id}"
                dest_abs_dir = os.path.join(settings.MEDIA_ROOT, dest_rel_dir)
                os.makedirs(dest_abs_dir, exist_ok=True)
                
                # ===== مسیر نهایی فایل ===== #
                dest_abs_path = os.path.join(dest_abs_dir, temp_name)
                
                shutil.move(temp_path, dest_abs_path)
                logger.debug(f"Moved file {temp_name} to {dest_abs_path}")
        
                final_paths[spec_id] = os.path.join(dest_rel_dir, temp_name)
            except ValueError:
                continue
            
        return final_paths