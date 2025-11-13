import logging
from celery import shared_task
from django.conf import settings

from core.common.email.email_service import EmailService

logger = logging.getLogger(__name__)

@shared_task(autoretry_for=(Exception,), retry_kwargs={"max_retries": 3, "countdown": 5})
def send_verification_email_task(user_email: str, verification_code: str):
    """
    یک تسک برای ارسال ایمیل فعال سازی برای کاربر
    """
    
    email_service = EmailService()
    logger.info(f"Sending verification email to address: {user_email}")
    try:
        email_service._send_email(
            subject="Printoo24 - کد تأیید حساب کاربری",
            template_name="email/verify_email.html",
            context={"verification_code": verification_code},
            from_email=settings.EMAIL_HOST_USER,
            to_email=user_email
        )
        logger.info(f"Email sent to address: {user_email}")
        return f"Email sent to address: {user_email}"
    except Exception as e:
        logger.error(f"Error sending email to address: {user_email} - {e}")
        raise e