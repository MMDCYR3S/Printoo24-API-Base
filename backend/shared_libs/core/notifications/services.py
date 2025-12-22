from typing import Optional
from django.contrib.contenttypes.models import ContentType

from .models import CustomerNotification
from core.models import User

# ========== NOTIFICATION SERVICE ========== #
class NotificationService:
    """
    سرویس دامنه برای مدیریت منطق مرکزی اعلان‌ها.
    """

    def send_notification(self, recipient: User, title: str, message: str, 
                          target_object: object, sender: Optional[User] = None) -> CustomerNotification:
        """
        ایجاد و ارسال یک اعلان جدید.
        این متد پیچیدگی GenericForeignKey را مخفی می‌کند.
        """
        # ===== دریافت ContentType به صورت پویا ===== #
        content_type = ContentType.objects.get_for_model(target_object)
        
        # ===== ایجاد اعلان ===== #
        return CustomerNotification.objects.create_notification({
            "recipient": recipient,
            "sender": sender,
            "name": title,
            "message": message,
            "content_type": content_type,
            "object_id": target_object.id,
            "is_read": False
        })
