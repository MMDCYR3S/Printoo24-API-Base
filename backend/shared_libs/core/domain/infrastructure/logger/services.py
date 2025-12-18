from typing import Any, Dict, Optional
from django.db import transaction
from django.conf import settings
from core.models import User, AuditLog
from .repositories import AuditLogRepository

class AuditLogDomainService:
    """
    سرویس دامنه برای ثبت وقایع.
    این سرویس باید در تمام سرویس‌های دیگر (Order, Product, User) اینجکت شود.
    """
    def __init__(self):
        self.repo = AuditLogRepository()
        
        self.SENSITIVE_FIELDS = {'password', 'token', 'refresh_token', 'credit_card'}

    @transaction.atomic
    def record_log(self, 
                   user: Optional[User], 
                   obj: Any, 
                   action: str, 
                   changes: Dict[str, Any] = None, 
                   description: str = "",
                   request_meta: Dict = None) -> AuditLog:
        """
        متد اصلی برای ثبت لاگ.
        
        :param request_meta: دیکشنری شامل IP و UserAgent (اگر در دسترس باشد)
        """
        if changes is None:
            changes = {}

        # ===== پاکسازی داده ها ===== #
        safe_changes = self._sanitize_changes(changes)

        # ===== دریافت اطلاعات meta ===== #
        ip = request_meta.get('REMOTE_ADDR') if request_meta else None
        ua = request_meta.get('HTTP_USER_AGENT') if request_meta else None

        # ===== ایجاد لاگ ===== #
        return self.repo.create_log(
            user=user,
            content_object=obj,
            action=action,
            changes=safe_changes,
            description=description,
            ip_address=ip,
            user_agent=ua
        )

    def get_history(self, obj: Any) -> list:
        """
        دریافت تاریخچه تغییرات یک آبجکت به فرمت مناسب برای نمایش در فرانت.
        """
        logs = self.repo.get_logs_for_object(obj)
        return logs

    def get_last_action_log(self, obj: Any, action: str = None) -> Optional[AuditLog]:
        """
        دریافت آخرین لاگ (معمولا برای لاجیک‌های محاسباتی مثل زمان توقف).
        """
        return self.repo.get_last_log_for_object(obj, action)

    # ================= Helper Methods ================= #
    def _sanitize_changes(self, changes: Dict[str, Any]) -> Dict[str, Any]:
        """
        حذف کلیدهای حساس از دیکشنری تغییرات.
        """
        clean_data = changes.copy()
        for key in list(clean_data.keys()):
            if key.lower() in self.SENSITIVE_FIELDS:
                clean_data[key] = "***REDACTED***"
        return clean_data
