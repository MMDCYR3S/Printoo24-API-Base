import os
from typing import Dict

from django.conf import settings
from django.core.files.base import ContentFile
from rest_framework.exceptions import ValidationError

from core.models import CartItem, CartItemUpload
# ====== File Finalize Service ====== #
class FileFinalizeService:
    """
    سرویس مسئول برای نهایی کردن فایل‌های موقت.
    در این مرحله فرض بر این است که فایل‌ها از نظر فنی (DPI/CMYK) سالم هستند.
    """
    
    def finalize_uploads(self, cart_item: CartItem, temp_file_names: Dict[str, str]):
        """
        :param temp_file_names: دیکشنری {requirement_id: temp_filename}
        """
        product = cart_item.product
        # ===== بررسی اینکه به تعداد فایل های محصول آپلود انجام شده است یا خیر ===== #
        required_specs = {str(req.file_spec.id): req for req in product.file_upload_requirements.filter(is_required=True)}

        
        # ===== اگر نیازی به آپلود نبود و آپلود انجام شد ===== #
        # ===== نکته: این بخش صرفاً برای صحیح بودن منطق کلی سیستم است. ===== #
        for spec_id, requirement in required_specs.items():
            if spec_id not in temp_file_names:
                raise ValidationError(f"فایل '{requirement.file_spec.name}' الزامی است.")

        # ===== بررسی و اعتبارسنجی آپلود فایل ===== #
        for spec_id, temp_filename in temp_file_names.items():
            temp_file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', 'temp', temp_filename)
            
            if not os.path.exists(temp_file_path):
                raise ValidationError(f"فایل موقت با نام {temp_filename} منقضی یا حذف شده است.")
            
            # ===== ذخیره فایل اعتبارسنجی شده ===== #
            try:
                requirement = product.file_upload_requirements.get(file_spec_id=spec_id)
                
                final_upload = CartItemUpload(
                    cart_item=cart_item,
                    requirement=requirement
                )
                
                with open(temp_file_path, 'rb') as file_data:
                    final_upload.file.save(temp_filename, ContentFile(file_data.read()), save=True)
                os.remove(temp_file_path)
            # ===== بروز خطا و حذف فایل موقت ===== #
            except ValidationError:
                raise
            except Exception as e:
                if os.path.exists(temp_file_path):
                   os.remove(temp_file_path)
                raise ValidationError(f"خطا در پردازش فایل '{temp_filename}': {str(e)}")
            