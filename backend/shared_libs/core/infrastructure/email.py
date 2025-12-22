from typing import Any, Optional

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

# ======= Email Service ======= #
class EmailService:
    """
    سرویس ارسال ایمیل
    """
    
    def _send_email(self, subject: str, template_name: str, context: dict, from_email: str,to_email: str) -> None:
        """
        ارسال ایمیل به کاربر مورد نظر با توجه به عملیاتی که قبل از آن انجام شده
        """
        html_message = render_to_string(template_name, context)
        plain_message = strip_tags(html_message)
        try:
            send_mail(
                subject = subject,
                message=plain_message,
                from_email=from_email,
                recipient_list=[to_email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            print(e)
