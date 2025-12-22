from typing import Optional, List
from django.db.models import QuerySet
from django.contrib.contenttypes.models import ContentType

from .models import CustomerNotification
from core.models import User

# ========== NOTIFICATION SERVICE ========== #
class NotificationService:
    """
    سرویس دامنه برای مدیریت منطق مرکزی اعلان‌ها.
    شامل متدهای خواندن (Read) و نوشتن (Write).
    """

    # ===== Write Operations ===== #
    def send_notification(self, recipient: User, title: str, message: str, 
                          target_object: object, sender: Optional[User] = None) -> CustomerNotification:
        """
        ایجاد و ارسال یک اعلان جدید.
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

    # ===== Read Operations (Proxy to Manager) ===== #
    def get_user_notifications(self, user: User, unread_only: bool = False) -> QuerySet[CustomerNotification]:
        """
        دریافت لیست اعلان‌های کاربر.
        """
        return CustomerNotification.objects.get_user_notifications(user, unread_only)

    def get_unread_count(self, user: User) -> int:
        """
        تعداد پیام‌های ناخوانده.
        """
        return CustomerNotification.objects.get_unread_count(user)

    def mark_all_as_read(self, user: User):
        """
        خواندن همه پیام‌ها.
        """
        CustomerNotification.objects.mark_all_as_read(user)
    
    def get_by_id(self, notification_id: int) -> Optional[CustomerNotification]:
        """
        دریافت اعلان با ID (برای استفاده در سرویس‌های دیگر).
        """
        try:
            return CustomerNotification.objects.get(id=notification_id)
        except CustomerNotification.DoesNotExist:
            return None
    