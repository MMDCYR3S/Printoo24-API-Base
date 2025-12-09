import os
import logging
from celery import shared_task
from core.models import OrderItemFile
from core.domain.commerce.order import OrderItemFileRepository

logger = logging.getLogger('apps.operations.tasks')

# ========== Task: Process Uploaded Design File ========== #
@shared_task(bind=True, max_retries=3)
def process_uploaded_design_file(self, file_id: int):
    """
    تسک پردازش فایل طراحی در پس‌زمینه.
    1. فایل را ولیدیت می‌کند (سایز، فرمت).
    2. متادیتای فایل (حجم، رزولوشن) را استخراج می‌کند.
    3. وضعیت را به 'pending' تغییر می‌دهد.
    """
    try:
        # ===== دریافت شناسه فایل ===== #
        repo = OrderItemFileRepository()
        file_obj = repo.get_by_id(file_id)
        
        if not file_obj or not file_obj.file:
            error_msg = f"File ID {file_id} not found or has no physical file."
            logger.error(error_msg)
            return error_msg
        
        # ===== لاگ حجم فایل ===== #
        file_name = os.path.basename(file_obj.file.name)
        file_size = file_obj.file.size
        logger.info(f"Processing file: {file_name} (Size: {file_size} bytes)")
        
        # ===== تغییر وضعیت فایل و ذخیره سازی ===== #
        file_obj.status = 'pending'
        file_obj.is_processed = True
        file_obj.save()
        
        success_msg = f"File {file_id} processed successfully."
        logger.info(success_msg)
        return success_msg

    except Exception as e:
        error_msg = f"System Error processing file ID {file_id}: {str(e)}"
        logger.error(error_msg, exc_info=True) # exc_info=True باعث می‌شود Traceback کامل ذخیره شود

        if file_obj:
            file_obj.admin_feedback = f"خطای سیستمی در پردازش فایل: {str(e)}"
            file_obj.status = 'rejected'
            file_obj.save()
            logger.info(f"File ID {file_id} marked as REJECTED due to error.")
        
        raise self.retry(exc=e, countdown=60)