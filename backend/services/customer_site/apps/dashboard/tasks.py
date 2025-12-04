import os
import logging
from celery import shared_task

from django.conf import settings
from django.core.files import File
from django.contrib.auth import get_user_model

from core.domain.email.email_services import EmailService 
from core.domain.product import ProductMediaDomainService

User = get_user_model()
logger = logging.getLogger('dashboard.tasks')

# ===== Task: Send Reply Email ===== #
@shared_task(name="send_contact_us_reply")
def send_contact_us_reply_task(user_email: str, user_name: str, reply_message: str, original_subject: str):
    """
    این تسک مسئول ارسال ایمیل پاسخ به کاربر است.
    تمام پارامترها باید سریالایزبل (Json Serializable) باشند (پس آبجکت مدل پاس نده).
    """
    email_service = EmailService()
    
    subject = f"پاسخ به پیام شما: {original_subject}"
    
    context = {
        'name': user_name,
        'reply_message': reply_message,
        'original_subject': original_subject,
        'site_name': "پرینتو24"
    }

    try:
        email_service._send_email(
            subject=subject,
            template_name="emails/contact_reply.html",
            context=context,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to_email=user_email
        )
        return f"Email sent to {user_email}"
    except Exception as e:
        return f"Failed to send email: {str(e)}"

# ===== Task: Upload Product Image ===== #
@shared_task(name='upload_product_image_task', bind=True, max_retries=3)
def upload_product_image_task(self, product_id, user_id, temp_file_path, original_filename):
    """ تسک آپلود تصویر محصول """
    logger.info(f"[Image Task] Starting for Product {product_id}. File: {temp_file_path}")
    media_service = ProductMediaDomainService()
    
    try:
        user = User.objects.get(id=user_id)

        if os.path.exists(temp_file_path):
            with open(temp_file_path, 'rb') as f:
                django_file = File(f, name=original_filename)
                instance = media_service.upload_product_image(product_id, user, django_file)
            
            # ===== حذف فایل موقت ===== #
            os.remove(temp_file_path)
            logger.info(f"[Image Task] Success: Image {instance.id} created.")
            return f"Image uploaded: {instance.id}"
        else:
            error_msg = f"[Image Task] File NOT FOUND at {temp_file_path}. Check Docker Volumes!"
            logger.error(error_msg)
            return "Temp file missing"

    except Exception as e:
        logger.error(f"[Image Task] Error: {str(e)}")
        raise self.retry(exc=e, countdown=60)

# ===== Task: Upload Attachment to Library ===== #
@shared_task(name='upload_attachment_library_task', bind=True, max_retries=3)
def upload_attachment_library_task(self, user_id, temp_file_path, original_filename, name_in_library):
    """ تسک آپلود فایل در کتابخانه """
    logger.info(f"[Attachment Task] Starting upload: {name_in_library}")
    media_service = ProductMediaDomainService()
    
    try:
        user = User.objects.get(id=user_id)
        
        if os.path.exists(temp_file_path):
            with open(temp_file_path, 'rb') as f:
                django_file = File(f, name=original_filename)
                instance = media_service.upload_attachment_to_library(user, django_file, name_in_library)
            
            os.remove(temp_file_path)
            logger.info(f"[Attachment Task] Success: Attachment {instance.id} created.")
            return f"Attachment uploaded: {instance.id}"
        else:
            logger.error(f"[Attachment Task] File NOT FOUND at {temp_file_path}")
            return "Temp file missing"

    except Exception as e:
        logger.error(f"[Attachment Task] Error: {str(e)}")
        raise self.retry(exc=e, countdown=60)