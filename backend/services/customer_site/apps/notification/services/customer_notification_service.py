import logging
from typing import Dict, Any, List
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound

from core.models import User, CustomerNotification
from core.domain.communication.notification.repositories import NotificationRepository

# ===== تعریف لاگر اختصاصی ===== #
logger = logging.getLogger('userprofile.services.notification')

class NotificationAppService:
    """
    سرویس اپلیکیشن برای مدیریت اعلان‌های کاربر در پنل کاربری.
    """
    
    def __init__(self, user: User):
        self.user = user
        self._repo = NotificationRepository()

    def get_my_notifications(self) -> List[CustomerNotification]:
        """
        دریافت لیست کامل اعلان‌های کاربر.
        """
        logger.info(f"Fetching notifications for User ID: {self.user.id}")
        
        try:
            notifications = self._repo.get_user_notifications(self.user)
            logger.debug(f"Found {notifications.count()} notifications for User ID: {self.user.id}")
            return notifications
            
        except Exception as e:
            logger.exception(f"Error fetching notifications for User ID: {self.user.id}")
            raise e

    def get_unread_count(self) -> int:
        """
        تعداد پیام‌های ناخوانده.
        """
        return self._repo.get_unread_count(self.user)

    def mark_as_read(self, notification_id: int) -> CustomerNotification:
        """
        تغییر وضعیت یک اعلان خاص به خوانده شده.
        """
        logger.info(f"Marking notification {notification_id} as read for User ID: {self.user.id}")
        
        try:
            # ===== یافتن اعلان با بررسی مالکیت ===== #
            notification = self._repo.model.objects.get(id=notification_id, recipient=self.user)
            
            notification.mark_as_read()
            logger.info(f"Notification {notification_id} marked as read.")
            return notification
            
        except CustomerNotification.DoesNotExist:
            logger.warning(f"Notification {notification_id} not found for User ID: {self.user.id}")
            raise NotFound("اعلان یافت نشد.")
            
        except Exception as e:
            logger.exception(f"Error updating notification {notification_id}")
            raise e

    def mark_all_read(self):
        """
        خواندن همه پیام‌ها.
        """
        logger.info(f"Marking ALL notifications as read for User ID: {self.user.id}")
        self._repo.mark_all_as_read(self.user)