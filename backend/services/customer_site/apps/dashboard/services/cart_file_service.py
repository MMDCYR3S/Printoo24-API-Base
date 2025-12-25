import os
import uuid
import logging
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.files import File
from kombu.exceptions import OperationalError

from apps.cart.models import CartItem, CartItemUpload

# ===== اصلاح مسیر ایمپورت ===== #
try:
    from apps.dashboard.tasks import upload_cart_item_file_task
except ImportError as e:
    print(f"Warning: Could not import upload task: {e}")
    upload_cart_item_file_task = None

logger = logging.getLogger('cart.services.file_upload')

# ===== Cart File Service ===== #
class CartFileService:
    def __init__(self):
        # مطمئن می‌شویم پوشه وجود دارد
        self.temp_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'temp_cart_uploads'))

    def _save_temp_file(self, file_obj) -> str:
        if not os.path.exists(self.temp_storage.location):
            try:
                os.makedirs(self.temp_storage.location)
            except OSError as e:
                logger.error(f"Failed to create temp directory: {e}")
                raise e
        
        ext = os.path.splitext(file_obj.name)[1]
        unique_name = f"{uuid.uuid4()}{ext}"
        saved_path = self.temp_storage.save(unique_name, file_obj)
        return self.temp_storage.path(saved_path)

    def upload_file_async(self, cart_item_id: int, requirement_id: int, file_obj):
        """
        آپلود فایل برای آیتم سبد خرید (Async + Sync Fallback).
        """
        logger.info(f"START: Upload request for CartItem {cart_item_id}, Requirement {requirement_id}")
        
        try:
            temp_path = self._save_temp_file(file_obj)
            original_name = file_obj.name
            logger.debug(f"Temp file saved at: {temp_path}")
        except Exception as e:
            logger.error(f"FAILED: Could not save temp file. Error: {e}", exc_info=True)
            raise e

        # تلاش برای ارسال به سلری
        try:
            if upload_cart_item_file_task:
                logger.info(f"Queuing async task for CartItem {cart_item_id}")
                upload_cart_item_file_task.delay(
                    cart_item_id=cart_item_id,
                    requirement_id=requirement_id,
                    temp_file_path=temp_path,
                    original_filename=original_name
                )
                return {"status": "processing", "detail": "File upload queued"}
            else:
                logger.warning("Celery task is not imported. Switching to SYNC mode immediately.")
                raise OperationalError("Task not imported")

        except (OperationalError, Exception) as e:
            logger.warning(f"ASYNC FAILED: {str(e)}. Switching to SYNC fallback.")
            
            # === FALLBACK (SYNC) === #
            try:
                logger.info("START: Sync upload fallback")
                cart_item = CartItem.objects.get(id=cart_item_id)
                
                existing_uploads = CartItemUpload.objects.filter(
                    cart_item=cart_item
                )
                for upload in existing_uploads:
                    if upload.file:
                        upload.file.delete(save=False)
                    upload.delete()
                
                if not os.path.exists(temp_path):
                     raise FileNotFoundError(f"Temp file missing at {temp_path}")

                with open(temp_path, 'rb') as f:
                    django_file = File(f, name=original_name)
                    instance = CartItemUpload.objects.create(
                        cart_item=cart_item,
                        file=django_file
                    )
                
                # حذف فایل موقت
                os.remove(temp_path)
                logger.info(f"SUCCESS: Sync upload completed. ID: {instance.id}")
                return {"status": "completed", "id": instance.id}
                
            except Exception as sync_error:
                # لاگ حیاتی برای فهمیدن دلیل خرابی نهایی
                logger.critical(f"SYNC FAILED: Could not upload file. Error: {str(sync_error)}", exc_info=True)
                
                # تلاش برای پاک کردن فایل موقت در صورت خرابی
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    
                raise sync_error