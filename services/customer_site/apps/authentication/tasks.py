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
    
@shared_task(autoretry_for=(Exception,), retry_kwargs={"max_retries": 3, "countdown": 5})
def send_password_reset_email_task(user_email:str, reset_link: str):
    """
    ارسال ایمیل بازنشانی رمز عبور به کاربر
    """
    
    email_service = EmailService()
    try:
        logger.info(f"Sending password reset email to address: {user_email}")
        email_service._send_email(
            subject="Printoo24 - بازنشانی رمز عبور",
            template_name="email/send_reset_password_email.html",
            context={"reset_link": reset_link},
            from_email=settings.EMAIL_HOST_USER,
            to_email=user_email,
        )
        logger.info(f"Password reset email sent to address: {user_email}")
        return f"Password reset email sent to address: {user_email}"
    except Exception as e:
        logger.error(f"Error sending email to address: {user_email} - {e}")
        raise e