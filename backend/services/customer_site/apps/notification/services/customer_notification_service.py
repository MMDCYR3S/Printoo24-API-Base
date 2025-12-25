import logging
from typing import List
from rest_framework.exceptions import NotFound

from core.models import User
from apps.notification.models import CustomerNotification
from apps.notification.domain_services import NotificationService

# ===== تعریف لاگر اختصاصی ===== #
logger = logging.getLogger('userprofile.services.notification')

# ========== NOTIFICATION SERVICE ========== #
class NotificationAppService:
    """
    سرویس اپلیکیشن برای مدیریت اعلان‌های کاربر در پنل کاربری.
    """
    
    def __init__(self, user: User):
        self.user = user
        self.domain_service = NotificationService()

    def get_my_notifications(self) -> List[CustomerNotification]:
        """
        دریافت لیست کامل اعلان‌های کاربر.
        """
        logger.info(f"Fetching notifications for User ID: {self.user.id}")
        
        try:
            # اکنون این متد در دامین سرویس وجود دارد
            notifications = self.domain_service.get_user_notifications(self.user)
            logger.debug(f"Found {notifications.count()} notifications for User ID: {self.user.id}")
            return notifications
            
        except Exception as e:
            logger.exception(f"Error fetching notifications for User ID: {self.user.id}")
            raise e

    def get_unread_count(self) -> int:
        """
        تعداد پیام‌های ناخوانده.
        """
        return self.domain_service.get_unread_count(self.user)

    def mark_as_read(self, notification_id: int) -> CustomerNotification:
        """
        تغییر وضعیت یک اعلان خاص به خوانده شده.
        """
        logger.info(f"Marking notification {notification_id} as read for User ID: {self.user.id}")
        
        try:
            # ===== یافتن اعلان با بررسی مالکیت ===== #
            # نکته: اینجا مستقیماً از مدل استفاده می‌کنیم چون یک کوئری خاص است که در سرویس دامین نیست
            # یا می‌توانیم یک متد get_my_notification در دامین اضافه کنیم.
            # فعلاً مستقیم:
            notification = CustomerNotification.objects.get(id=notification_id, recipient=self.user)
            
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
        self.domain_service.mark_all_as_read(self.user)
