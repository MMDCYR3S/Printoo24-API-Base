import os
import logging
from celery import shared_task

from django.conf import settings
from django.core.files import File
from django.contrib.auth import get_user_model

from core.infrastructure import EmailService 
from core.product.services import ProductMediaService
from core.models import (
    OrderItem,
    OrderItemFile
)
from apps.cart.models import CartItem, CartItemUpload

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
def upload_product_image_task(self, product_id, user_id, temp_file_path, original_filename, order=0):
    """ تسک آپلود و فشرده‌سازی همزمان تصویر محصول """
    logger.info(f"[Image Task] Starting for Product {product_id}. File: {temp_file_path}")
    media_service = ProductMediaService()

    try:
        user = User.objects.get(id=user_id)

        if not os.path.exists(temp_file_path):
            logger.error(f"[Image Task] File NOT FOUND at {temp_file_path}. Check Docker Volumes!")
            return "Temp file missing"

        # ===== فشرده‌سازی قبل از آپلود ===== #
        from apps.shop.tasks import _compress_image_bytes
        compressed_bytes, ext = _compress_image_bytes(temp_file_path)
        stem = os.path.splitext(original_filename)[0]
        compressed_filename = f"{stem}{ext}"

        # ===== آپلود فایل فشرده ===== #
        with open(temp_file_path, 'rb') as _:
            from django.core.files.base import ContentFile
            django_file = File(ContentFile(compressed_bytes), name=compressed_filename)
            instance = media_service.upload_product_image(product_id, user, django_file, order)

        # ===== حذف فایل موقت ===== #
        os.remove(temp_file_path)
        logger.info(f"[Image Task] Success: Image {instance.id} uploaded & compressed.")
        return f"Image uploaded & compressed: {instance.id}"

    except Exception as e:
        logger.error(f"[Image Task] Error: {str(e)}")
        raise self.retry(exc=e, countdown=60)

# ===== Task: Upload Attachment to Library ===== #
@shared_task(name='upload_attachment_library_task', bind=True, max_retries=3)
def upload_attachment_library_task(self, user_id, product_id, temp_file_path, original_filename, name_in_library):
    """ تسک آپلود فایل در کتابخانه """
    logger.info(f"[Attachment Task] Starting upload: {name_in_library}")
    media_service = ProductMediaService()
    try:
        user = User.objects.get(id=user_id)

        if os.path.exists(temp_file_path):
            with open(temp_file_path, 'rb') as f:
                django_file = File(f, name=original_filename)
                instance = media_service.upload_attachment_to_library(user, django_file, product_id, name_in_library)
            
            os.remove(temp_file_path)
            logger.info(f"[Attachment Task] Success: Attachment {instance.id} created.")
            return f"Attachment uploaded: {instance.id}"
        else:
            logger.error(f"[Attachment Task] File NOT FOUND at {temp_file_path}")
            return "Temp file missing"

    except Exception as e:
        logger.error(f"[Attachment Task] Error: {str(e)}")
        raise self.retry(exc=e, countdown=60)
    
logger = logging.getLogger('cart.tasks')

# ===== Task: Upload Cart Item File ===== #
@shared_task(name='upload_cart_item_file_task', bind=True, max_retries=3)
def upload_cart_item_file_task(self, cart_item_id, temp_file_path, original_filename):
    """
    تسک آپلود فایل طراحی توسط کاربر برای یک آیتم سبد خرید.
    """
    logger.info(f"[Cart Upload Task] Starting for Item {cart_item_id}")
    
    try:
        # ===== دریافت آیتم ===== #
        cart_item = CartItem.objects.get(id=cart_item_id)

        # ===== بررسی وجود فایل از قبل و جایگزینی ===== #
        existing_uploads = CartItemUpload.objects.filter(
            cart_item=cart_item
        )
        
        for upload in existing_uploads:
            # ===== حذف فایل ها ===== #
            if upload.file:
                upload.file.delete(save=False)
            upload.delete()

        # ===== ایجاد فایل ===== #
        if os.path.exists(temp_file_path):
            with open(temp_file_path, 'rb') as f:
                django_file = File(f, name=original_filename)
                
                # ===== ایجاد آیتم ===== #
                upload_instance = CartItemUpload.objects.create(
                    cart_item=cart_item,
                    file=django_file
                )
            
            # ===== حذف فایل موقت ===== #
            os.remove(temp_file_path)
            logger.info(f"[Cart Upload Task] Success: Upload {upload_instance.id} created.")
            return f"File uploaded: {upload_instance.id}"
        else:
            logger.error(f"[Cart Upload Task] File NOT FOUND at {temp_file_path}")
            return "Temp file missing"

    except Exception as e:
        logger.error(f"[Cart Upload Task] Error: {str(e)}")
        raise self.retry(exc=e, countdown=60)

# ===== Task: Upload Order Item File ===== #
@shared_task(name='upload_order_item_file_task', bind=True, max_retries=3)
def upload_order_item_file_task(self, order_item_id, temp_file_path, original_filename):
    """
    تسک آپلود فایل طراحی توسط ادمین برای یک آیتم سفارش.
    """
    logger.info(f"[Order Upload Task] Starting for OrderItem {order_item_id}")
    
    try:
        # ===== دریافت مدل ها ===== #
        order_item = OrderItem.objects.get(id=order_item_id)
        
        # ===== بررسی وجود فایل از قبل و جایگزینی ===== #
        existing_uploads = OrderItemFile.objects.filter(
            order_item=order_item
        )
        
        for upload in existing_uploads:
            # ===== حذف فایل ها ===== #
            if upload.file:
                upload.file.delete(save=False)
            upload.delete()

        # ===== دریافت فایل ===== #
        if os.path.exists(temp_file_path):
            with open(temp_file_path, 'rb') as f:
                django_file = File(f, name=original_filename)
                
                # ===== ایجاد فایل===== #
                instance = OrderItemFile.objects.create(
                    order_item=order_item,
                    file=django_file
                )
            
            # ===== پاک کردن فایل temp ===== #
            os.remove(temp_file_path)
            logger.info(f"[Order Upload Task] Success: File {instance.id} attached to OrderItem {order_item_id}.")
            return f"File uploaded: {instance.id}"
        else:
            error_msg = f"[Order Upload Task] Temp file NOT FOUND at {temp_file_path}"
            logger.error(error_msg)
            return "Temp file missing"

    except Exception as e:
        logger.error(f"[Order Upload Task] Error: {str(e)}", exc_info=True)
        raise self.retry(exc=e, countdown=60)
    