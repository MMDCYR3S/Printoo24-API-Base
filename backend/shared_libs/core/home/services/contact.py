from celery import current_app
from django.utils import timezone
from django.core.exceptions import ValidationError

from ..models import ContactUs

# ========== CONTACT SERVICE ========== #
class ContactService:
    """
    سرویس مدیریت پیام‌های تماس با ما.
    """

    def submit_contact_form(self, data: dict) -> ContactUs:
        """
        ثبت پیام تماس با ما.
        """
        return ContactUs.objects.create_message(data)

    def reply_to_user_message(self, message_id: int, reply_text: str, admin_user=None):
        """
        پاسخ به پیام کاربر و ارسال ایمیل.
        """
        message = ContactUs.objects.get_by_id(message_id)
        if not message:
            raise ValidationError("پیام مورد نظر یافت نشد.")
            
        # ===== جلوگیری از پاسخ مجدد ===== #
        if message.admin_reply:
            raise ValidationError("به این پیام قبلاً پاسخ داده شده است.")

        if not message.email:
             raise ValidationError("کاربر ایمیل ندارد، امکان ارسال پاسخ نیست.")

        # ===== ذخیره پاسخ و تغییر وضعیت ===== #
        message.is_read = True
        message.admin_reply = reply_text
        message.replied_at = timezone.now()
        if admin_user:
            message.replied_by = admin_user
            
        message.save()

        # ===== ارسال تسک ایمیل ===== #
        current_app.send_task(
            'send_contact_us_reply',
            kwargs={
                'user_email': message.email,
                'user_name': message.full_name,
                'reply_message': reply_text,
                'original_subject': message.subject
            }
        )

        return message
