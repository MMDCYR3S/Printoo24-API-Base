import os
from typing import Dict

from django.conf import settings
from django.core.files.base import ContentFile
from rest_framework.exceptions import ValidationError

from core.models import CartItem, CartItemUpload

# ====== File Finalize Service ====== #
class FileFinalizeService:
    """
    سرویس مسئول برای نهایی کردن فایل‌های موقت (ذخیره شده در فایل سیستم)
    و اتصال آن‌ها به یک آیتم سبد خرید.
    """
    
    def finalize_uploads(self, cart_item: CartItem, temp_file_names: Dict[str, str]):
        """
        فایل‌های موقت را بر اساس نامشان پیدا کرده، به مسیر نهایی منتقل
        و فایل موقت را از دیسک پاک می‌کند.
        
        :param cart_item: آیتم سبد خریدی که فایل‌ها به آن متصل می‌شوند.
        :param temp_file_names: دیکشنری از {spec_id: temp_file_name}.
        """
        product = cart_item.product
        required_specs = {str(req.file_spec.id): req for req in product.file_upload_requirements.filter(is_required=True)}

        
        # ===== اگر نیازی به آپلود نبود و آپلود انجام شد ===== #
        # ===== نکته: این بخش صرفاً برای صحیح بودن منطق کلی سیستم است. ===== #
        for spec_id, requirement in required_specs.items():
            if spec_id not in temp_file_names:
                raise ValidationError(f"فایل '{requirement.file_spec.name}' الزامی است و باید آپلود شود.")

        # ===== بررسی و اعتبارسنجی آپلود فایل ===== #
        for spec_id, temp_filename in temp_file_names.items():
            temp_file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', 'temp', temp_filename)
            
            if not os.path.exists(temp_file_path):
                raise ValidationError(f"فایل موقت با نام {temp_filename} یافت نشد. لطفاً دوباره آپلود کنید.")
            
            # ===== ذخیره فایل ===== #
            try:
                requirement = product.file_upload_requirements.get(file_spec_id=spec_id)
                # ===== افزودن فایل به مدل ===== #
                final_upload = CartItemUpload(
                    cart_item=cart_item,
                    requirement=requirement
                )
                
                with open(temp_file_path, 'rb') as file_data:
                    final_upload.file.save(temp_filename, ContentFile(file_data.read()), save=True)
                    
                os.remove(temp_file_path)
                
            except Exception as e:
                os.remove(temp_file_path)
                raise ValidationError(f"خطا در پردازش فایل: {str(e)}")
            