from django.db import models

# ========== BASE QUERYSET ========== #
class BaseQuerySet(models.QuerySet):
    def get_by_id(self, id: int):
        return self.filter(id=id).first()

# ========== NITIFICATION QUERYSET ========== #
class NotificationQuerySet(BaseQuerySet):
    """
    کوئری‌های مربوط به اعلان‌ها
    """
    
    def get_user_notifications(self, user, unread_only: bool = False):
        """
        دریافت لیست اعلان‌های کاربر.
        """
        queryset = self.filter(recipient=user)
        if unread_only:
            queryset = queryset.filter(is_read=False)
        return queryset

    def get_unread_count(self, user) -> int:
        """
        دریافت تعداد اعلان‌های خوانده نشده.
        """
        return self.filter(recipient=user, is_read=False).count()

    def mark_all_as_read(self, user):
        """
        خواندن تمام پیام‌های کاربر (Bulk Update).
        """
        self.filter(recipient=user, is_read=False).update(is_read=True)

# ========== NITIFICATION MANAGER ========== #
class NotificationManager(models.Manager):
    def get_queryset(self):
        return NotificationQuerySet(self.model, using=self._db)

    def get_user_notifications(self, user, unread_only: bool = False):
        return self.get_queryset().get_user_notifications(user, unread_only)

    def get_unread_count(self, user):
        return self.get_queryset().get_unread_count(user)

    def mark_all_as_read(self, user):
        return self.get_queryset().mark_all_as_read(user)
    
    def create_notification(self, data):
        return self.create(**data)
