from typing import List
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from core.models import Order, User
from apps.support.services import LoggerService
from apps.permissions import AppPermissionChecker

# ========== Order List App Service ========== #
class OrderListAppService:
    """
    سرویس نمایش لیست سفارشات براساس نقش کارمند (Role-Based Filtering).
    این سرویس تضمین می‌کند که هر کارمند فقط سفارشاتی را ببیند که به مرحله (Stage)
    مرتبط با نقش او رسیده‌اند (مگر اینکه ادمین کل باشد).
    """
    def __init__(self):
        self.audit_service = LoggerService()

    def get_order_list_for_staff(self, requester: User) -> List[Order]:
        """
        دریافت لیست سفارشات فیلتر شده بر اساس نقش کارمند.
        """
        # ===== چک کردن دسترسی ===== #
        AppPermissionChecker.check_has_permission(requester, 'view_order')
        # ===== نمایش سفارشات کلی براساس نقش ===== #
        queryset = Order.objects.get_all_orders_summary()
        
        role_slug = 'unknown'
        final_qs = Order.objects.none()
        
        # ===== فیلترینگ براساس نقش ===== #
        if requester.is_superuser:
            role_slug = 'superuser'
            final_qs = queryset
            
        else:
            # ===== بررسی وجود نقش برای کاربر ===== #
            user_role_rel = requester.user_role.select_related('role').first()
            if not user_role_rel:
                return Order.objects.none()
            
            # ===== دریافت نقش کاربر ===== #
            role = user_role_rel.role
            role_slug = role.slug
            # ===== دریافت گروه‌های مرتبط با نقش ===== #
            allowed_groups = list(role.allowed_groups.values_list('code', flat=True))

            if role.type == "admin" or allowed_groups:
                final_qs = queryset.filter(current_status__group__code__in=allowed_groups)
            else:
                final_qs = Order.objects.none()

        # ===== ثبت لاگ مشاهده لیست ===== #
        self.audit_service.record_log(
            user=requester,
            obj=None,
            action='VIEW_ORDER_LIST',
            changes={'role_used': role_slug, 'count': final_qs.count()},
            description=_("مشاهده کارتابل سفارشات")
        )

        return final_qs
