from celery import shared_task
from django.conf import settings
from core.domain.email.email_services import EmailService 

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
