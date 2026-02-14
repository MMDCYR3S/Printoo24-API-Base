from typing import Dict, Any, Optional
from django.db.models import QuerySet
from rest_framework.exceptions import NotFound, PermissionDenied

from core.models import User, Order, OrderStateLog
from apps.permissions import AppPermissionChecker
from apps.order.domain_services import OrderStatusFlowService

# ========== ORDER HISTORY APP SERVICE ========== #
class OrderHistoryAppService:
    """
    سرویس اپلیکیشن جهت مشاهده تاریخچه و لاگ‌های سفارش توسط ادمین.
    """
    def __init__(self):
        self._domain_service = OrderStatusFlowService()

    # ===== SHOW ORDER HISTORY ===== #
    def get_order_history_details(self, user: User, order_id: int) -> Dict[str, Any]:
        """
        دریافت اطلاعات هدر سفارش + لیست تغییرات وضعیت.
        """
        # ===== بررسی دسترسی ===== #
        AppPermissionChecker.check_has_permission(user, 'view_order')

        # ===== دریافت سفارش ===== #
        try:
            order = Order.objects.select_related('current_status').get(pk=order_id)
        except Order.DoesNotExist:
            raise NotFound("سفارش مورد نظر یافت نشد.")

        # ===== دریافت لاگ‌ها ===== #
        logs = self._domain_service.get_order_state_logs(order_id)

        # ===== خروجی ترکیبی ===== #
        return {
            "order": order,
            "logs": logs
        }

    def get_all_logs(self, user: User, filters: Optional[dict] = None) -> QuerySet[OrderStateLog]:
        """
        دریافت تمام لاگ‌های سیستم برای نمایش در لیست کلی.
        شامل بهینه‌سازی کوئری برای جلوگیری از N+1.
        """
        # ===== بررسی دسترسی ===== #
        AppPermissionChecker.check_has_permission(user, 'view_order_logs')

        # ===== دریافت لاگ‌ها با بهینه‌سازی کوئری ===== #
        queryset = OrderStateLog.objects.select_related(
            'order',
            'actor',
            'from_status',
            'to_status'
        ).order_by('-created_at')

        return queryset
