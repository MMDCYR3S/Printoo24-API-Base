import os
import shutil
import logging
from typing import Dict

from django.conf import settings
from rest_framework.exceptions import ValidationError

logger = logging.getLogger('cart.services.cart_file')

class FileFinalizeService:
    """
    سرویس نهایی‌سازی فایل‌ها: انتقال از Temp به User Directory.
    """
    
    def finalize_files(self, temp_files_map: Dict[str, str], user_id: int) -> Dict[int, str]:
        """
        Args:
            temp_files_map: {requirement_id (str): temp_filename (str)}
        Returns:
            {requirement_id (int): relative_path_in_media (str)}
        """
        final_paths = {}
        
        for req_id_str, temp_name in temp_files_map.items():
            try:
                req_id = int(req_id_str)
                
                # مسیر فایل موقت
                temp_path = os.path.join(settings.MEDIA_ROOT, 'uploads', 'temp', temp_name)
                
                if not os.path.exists(temp_path):
                    logger.error(f"Temp file missing during finalize: {temp_path}")
                    # اینجا بسته به بیزنس لاجیک می‌توانید خطا دهید یا نادیده بگیرید
                    # اگر خطا بدهیم، کل پروسه افزودن به سبد خرید رول‌بک می‌شود (چون اتمیک است)
                    raise ValidationError(f"فایل آپلود شده {temp_name} منقضی یا حذف شده است. لطفاً مجدداً آپلود کنید.")
                
                # ساختار پوشه بندی: media/cart_uploads/USER_ID/
                dest_rel_dir = f"cart_uploads/{user_id}"
                dest_abs_dir = os.path.join(settings.MEDIA_ROOT, dest_rel_dir)
                os.makedirs(dest_abs_dir, exist_ok=True)
                
                # انتقال فایل
                dest_abs_path = os.path.join(dest_abs_dir, temp_name)
                shutil.move(temp_path, dest_abs_path)
                
                # مسیر نسبی برای ذخیره در دیتابیس
                final_paths[req_id] = os.path.join(dest_rel_dir, temp_name)
                
                logger.debug(f"Finalized file for req {req_id}: {final_paths[req_id]}")
                
            except ValueError:
                logger.warning(f"Invalid requirement ID format: {req_id_str}")
                continue
            except OSError as e:
                logger.error(f"OS Error moving file {temp_name}: {e}")
                raise ValidationError("خطا در جابجایی فایل نهایی.")

        return final_paths