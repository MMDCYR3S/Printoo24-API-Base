from typing import Optional
from django.contrib.contenttypes.models import ContentType
from core.models import User, CustomerNotification
from .repositories import NotificationRepository

# ===== Notification Domain Service ===== #
class NotificationDomainService:
    """
    سرویس دامنه برای مدیریت منطق مرکزی اعلان‌ها.
    """
    def __init__(self):
        self.repo = NotificationRepository()

    def send_notification(self, recipient: User, title: str, message: str, 
                          target_object: object, sender: Optional[User] = None) -> CustomerNotification:
        """
        ایجاد و ارسال یک اعلان جدید.
        این متد پیچیدگی GenericForeignKey را مخفی می‌کند.
        
        Args:
            target_object: شیئی که اعلان درباره آن است (مثلاً Order یا Product).
        """
        # ===== دریافت ContentType به صورت پویا ===== #
        content_type = ContentType.objects.get_for_model(target_object)
        
        # ===== ایجاد اعلان از طریق ریپازیتوری ===== #
        return self.repo.create({
            "recipient": recipient,
            "sender": sender,
            "name": title,
            "message": message,
            "content_type": content_type,
            "object_id": target_object.id,
            "is_read": False
        })
