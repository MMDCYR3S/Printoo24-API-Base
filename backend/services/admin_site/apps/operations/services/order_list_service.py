from typing import List
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import PermissionDenied

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

    def get_order_list_for_staff(self, requester: User):
        """
        دریافت لیست سفارشات فیلتر شده بر اساس نقش کارمند و وضعیت‌های مجاز.
        """
        # ===== ۱. بررسی دسترسی پایه ===== #
        AppPermissionChecker.check_has_permission(requester, 'view_order')
        
        # ===== ۲. دریافت کوئری‌ست پایه (Summary) ===== #
        queryset = Order.objects.get_all_orders_summary()
        
        role_slug = 'unknown'
        is_full_admin = False

        # ===== ۳. تشخیص هویت و سطح دسترسی کاربر ===== #
        if requester.is_superuser:
            role_slug = 'superuser'
            is_full_admin = True
            final_qs = queryset
        else:
            user_role_rel = requester.user_role.select_related('role').first()
            if not user_role_rel:
                raise PermissionDenied(_("شما هیچ نقش سیستمی فعالی ندارید."))
            
            role = user_role_rel.role
            role_slug = role.slug
            
            if role.type == "admin":
                is_full_admin = True
                final_qs = queryset
            else:
                allowed_groups = list(role.allowed_groups.values_list('code', flat=True))
                if allowed_groups:
                    final_qs = queryset.filter(current_status__group__code__in=allowed_groups)
                else:
                    final_qs = Order.objects.none()

        # ===== ۴. اعمال فیلتر محدودکننده (Exclude Reject/Cancel) ===== #
        if not is_full_admin:
            final_qs = final_qs.exclude(
                current_status__status_type__in=['reject', 'cancel']
            )

        # ===== ۵. ثبت لاگ سیستم (Audit Log) ===== #
        self.audit_service.record_log(
            user=requester,
            obj=None,
            action='VIEW_ORDER_LIST',
            changes={'role_used': role_slug, 'count': final_qs.count(), 'is_admin': is_full_admin},
            description=_("مشاهده کارتابل سفارشات با اعمال فیلترهای دسترسی")
        )

        return final_qs
