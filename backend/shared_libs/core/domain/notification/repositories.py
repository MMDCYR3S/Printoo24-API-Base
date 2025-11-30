from typing import List
from django.db.models import QuerySet
from core.models import CustomerNotification, User
from core.utils.base_repository import BaseRepository

# ===== Nofitication Repository ===== #
class NotificationRepository(BaseRepository[CustomerNotification]):
    """
    ریپازیتوری مدیریت اعلان‌ها.
    """
    def __init__(self):
        super().__init__(CustomerNotification)

    def get_user_notifications(self, user: User, unread_only: bool = False) -> QuerySet[CustomerNotification]:
        """
        دریافت لیست اعلان‌های کاربر.
        """
        queryset = self.model.objects.filter(recipient=user)
        if unread_only:
            queryset = queryset.filter(is_read=False)
        return queryset

    def get_unread_count(self, user: User) -> int:
        """
        دریافت تعداد اعلان‌های خوانده نشده (برای نمایش بج در فرانت).
        """
        return self.model.objects.filter(recipient=user, is_read=False).count()

    def mark_all_as_read(self, user: User):
        """
        خواندن تمام پیام‌های کاربر (Bulk Update).
        """
        self.model.objects.filter(recipient=user, is_read=False).update(is_read=True)
