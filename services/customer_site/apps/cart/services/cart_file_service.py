import os
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
    
    def finalize_uploads(self, cart_item: CartItem, temp_file_names: Dict[str, str]):
        """
        پردازش و ذخیره نهایی فایل‌های موقت.

        Args:
            cart_item (CartItem): آیتم سبد خرید که فایل‌ها متعلق به آن هستند.
            temp_file_names (Dict[str, str]): دیکشنری شامل شناسه نیازمندی (spec_id) و نام فایل موقت.

        Raises:
            ValidationError: در صورت کمبود فایل‌های اجباری یا عدم وجود فایل موقت.
        """
        logger.info(f"Starting file finalization for CartItem ID: {cart_item.id}")
        
        product = cart_item.product
        
        # ===== استخراج نیازمندی‌های اجباری آپلود برای این محصول ===== #
        required_specs = {str(req.spec.id): req for req in product.file_upload_requirements.filter(is_required=True)}
        
        # ===== بررسی اینکه آیا تمام فایل‌های اجباری آپلود شده‌اند یا خیر ===== #
        for spec_id, requirement in required_specs.items():
            if spec_id not in temp_file_names:
                logger.warning(
                    f"Missing required file for CartItem ID: {cart_item.id}. "
                    f"Requirement: {requirement.spec.name}"
                )
                raise ValidationError(f"فایل '{requirement.spec.name}' الزامی است.")

        # ===== شروع پردازش و انتقال فایل‌ها ===== #
        for spec_id, temp_filename in temp_file_names.items():
            # ===== ساخت مسیر کامل فایل موقت ===== #
            temp_file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', 'temp', temp_filename)
            
            # ===== بررسی وجود فیزیکی فایل موقت ===== #
            if not os.path.exists(temp_file_path):
                logger.error(f"Temp file not found at path: {temp_file_path}")
                raise ValidationError(f"فایل موقت با نام {temp_filename} منقضی یا حذف شده است.")
            
            try:
                # ===== دریافت آبجکت نیازمندی مربوطه ===== #
                requirement = product.file_upload_requirements.get(spec_id=spec_id)
                
                # ===== ایجاد رکورد آپلود نهایی ===== #
                final_upload = CartItemUpload(
                    cart_item=cart_item,
                    requirement=requirement
                )
                
                # ===== کپی محتوا از فایل موقت به فیلد فایل مدل ===== #
                # نکته: متد save در فیلد FileField به صورت خودکار فایل را در مسیر نهایی ذخیره می‌کند
                with open(temp_file_path, 'rb') as file_data:
                    final_upload.file.save(temp_filename, ContentFile(file_data.read()), save=True)
                
                logger.info(f"File {temp_filename} saved successfully for CartItem ID: {cart_item.id}")

                # ===== حذف فایل موقت پس از ذخیره موفقیت‌آمیز ===== #
                os.remove(temp_file_path)
                logger.debug(f"Temp file removed: {temp_file_path}")
                
            except ValidationError as e:
                logger.warning(f"Validation error during file processing: {e}")
                raise e
            
            except Exception as e:
                # ===== مدیریت خطای سیستمی و پاکسازی ===== #
                logger.exception(f"Critical error processing file {temp_filename} for CartItem ID: {cart_item.id}")
                
                # تلاش برای حذف فایل موقت جهت جلوگیری از اشغال فضا در صورت بروز خطا
                if os.path.exists(temp_file_path):
                    try:
                        os.remove(temp_file_path)
                        logger.debug(f"Temp file removed after error: {temp_file_path}")
                    except OSError as os_err:
                        logger.error(f"Failed to remove temp file after error: {os_err}")

                raise ValidationError(f"خطا در پردازش فایل '{temp_filename}': {str(e)}")
