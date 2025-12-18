from typing import Optional, List, Dict, Any
from django.db.models import QuerySet
from django.contrib.contenttypes.models import ContentType
from core.utils.base_repository import BaseRepository
from core.models import AuditLog, User

class AuditLogRepository(BaseRepository[AuditLog]):
    """
    ریپازیتوری مرکزی برای مدیریت لاگ‌های سیستم.
    وظیفه اصلی: هندل کردن Query‌های مربوط به ContentType و CRUD پایه.
    """
    def __init__(self):
        super().__init__(AuditLog)

    def create_log(self, 
                   user: Optional[User], 
                   content_object: Any, 
                   action: str, 
                   changes: Dict[str, Any], 
                   description: str = "",
                   ip_address: str = None,
                   user_agent: str = None) -> AuditLog:
        """
        ایجاد رکورد لاگ.
        نکته: ContentType به صورت خودکار از content_object استخراج می‌شود.
        """
        return self.model.objects.create(
            user=user,
            content_object=content_object, # جنگو خودش content_type و object_id را پر می‌کند
            action=action,
            changes=changes,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent
        )

    def get_logs_for_object(self, obj: Any) -> QuerySet[AuditLog]:
        """
        دریافت تمام لاگ‌های مربوط به یک آبجکت خاص (مثلاً تاریخچه یک سفارش).
        """
        content_type = ContentType.objects.get_for_model(obj)
        return self.model.objects.filter(
            content_type=content_type,
            object_id=obj.id
        ).select_related('user').order_by('-timestamp')

    def get_last_log_for_object(self, obj: Any, action: str = None) -> Optional[AuditLog]:
        """
        دریافت آخرین لاگ ثبت شده برای یک آبجکت.
        کاربرد: محاسبه Duration در تغییر وضعیت‌ها.
        """
        content_type = ContentType.objects.get_for_model(obj)
        qs = self.model.objects.filter(
            content_type=content_type,
            object_id=obj.id
        )
        if action:
            qs = qs.filter(action=action)
            
        return qs.order_by('-timestamp').first()

    def get_user_activity(self, user: User, limit: int = 20) -> QuerySet[AuditLog]:
        """
        دریافت آخرین فعالیت‌های یک کاربر خاص.
        """
        return self.model.objects.filter(user=user).order_by('-timestamp')[:limit]
