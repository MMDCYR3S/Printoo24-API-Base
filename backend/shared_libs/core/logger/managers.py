from typing import Any
from django.db import models
from django.contrib.contenttypes.models import ContentType

# ========== LOGGER QUERYSET ========== #
class AuditLogQuerySet(models.QuerySet):
    """
    کوئری‌های مربوط به لاگ سیستم
    """
    
    def get_logs_for_object(self, obj: Any):
        """
        دریافت تمام لاگ‌های مربوط به یک آبجکت خاص.
        """
        content_type = ContentType.objects.get_for_model(obj)
        return self.filter(
            content_type=content_type,
            object_id=obj.id
        ).select_related('user').order_by('-timestamp')

    def get_last_log_for_object(self, obj: Any, action: str = None):
        """
        دریافت آخرین لاگ ثبت شده برای یک آبجکت.
        """
        content_type = ContentType.objects.get_for_model(obj)
        qs = self.filter(
            content_type=content_type,
            object_id=obj.id
        )
        if action:
            qs = qs.filter(action=action)
            
        return qs.order_by('-timestamp').first()

    def get_user_activity(self, user, limit: int = 20):
        """
        دریافت آخرین فعالیت‌های یک کاربر خاص.
        """
        return self.filter(user=user).order_by('-timestamp')[:limit]

# ========== LOGGER MANAGER ========== #
class AuditLogManager(models.Manager):
    def get_queryset(self):
        return AuditLogQuerySet(self.model, using=self._db)

    def create_log(self, user, content_object, action, changes, description="", ip_address=None, user_agent=None):
        """
        ایجاد رکورد لاگ.
        جنگو خودش content_type و object_id را از content_object پر می‌کند.
        """
        return self.create(
            user=user,
            content_object=content_object,
            action=action,
            changes=changes,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent
        )

    def get_logs_for_object(self, obj):
        return self.get_queryset().get_logs_for_object(obj)

    def get_last_log_for_object(self, obj, action=None):
        return self.get_queryset().get_last_log_for_object(obj, action)

    def get_user_activity(self, user, limit=20):
        return self.get_queryset().get_user_activity(user, limit)
