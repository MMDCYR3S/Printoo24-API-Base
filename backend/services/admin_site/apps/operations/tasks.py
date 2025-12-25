import os
import logging
from celery import shared_task
from core.models import OrderItemFile

# ========== Logger ========== #
logger = logging.getLogger('apps.operations.tasks')

# ========== Task: Process Uploaded Design File ========== #
@shared_task(bind=True, max_retries=3)
def process_uploaded_design_file(self, file_id: int):
    """
    تسک پردازش فایل طراحی در پس‌زمینه.
    1. فایل را از دیتابیس می‌خواند (بدون ریپازیتوری).
    2. متادیتای فایل (حجم، رزولوشن) را استخراج می‌کند (شبیه‌سازی).
    3. وضعیت را به‌روز می‌کند.
    """
    file_obj = None
    try:
        # ===== دریافت فایل با استفاده از منیجر ===== #
        try:
            file_obj = OrderItemFile.objects.get(id=file_id)
        except OrderItemFile.DoesNotExist:
            error_msg = f"File ID {file_id} not found."
            logger.error(error_msg)
            return error_msg
        
        if not file_obj.file:
            error_msg = f"File ID {file_id} has no physical file associated."
            logger.error(error_msg)
            return error_msg
        
        # ===== پردازش فایل (Validation/Metadata Extraction) ===== #
        file_name = os.path.basename(file_obj.file.name)
        file_size = file_obj.file.size
        
        logger.info(f"Processing file: {file_name} (Size: {file_size} bytes)")
        
        if hasattr(file_obj, 'is_processed'):
            file_obj.is_processed = True
        

        file_obj.save()
        
        success_msg = f"File {file_id} processed successfully."
        logger.info(success_msg)
        return success_msg

    except Exception as e:
        error_msg = f"System Error processing file ID {file_id}: {str(e)}"
        logger.error(error_msg, exc_info=True) 

        # ===== مدیریت خطا ===== #
        if file_obj:
            file_obj.admin_feedback = f"System Error: {str(e)}"
            
            if hasattr(file_obj, 'status'):
                file_obj.status = 'rejected'
                
            file_obj.save()
            logger.info(f"File ID {file_id} marked as FAILED due to error.")

        raise self.retry(exc=e, countdown=60)
