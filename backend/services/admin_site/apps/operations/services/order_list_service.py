from typing import List
from django.db.models import Q

from core.domain.commerce.order.main import OrderRepository
from core.models import Order, User, OrderItem, Role
from apps.permissions import AppPermissionChecker

# ========== Order List App Service ========== #
class OrderListAppService:
    """
    سرویس نمایش لیست سفارشات براساس نوع نقش و مجوز دسترسی
    """
    def __init__(self):
        self.repo = OrderRepository()

    def get_order_list_for_staff(self, requester: User) -> List[Order]:
        """
        دریافت لیست سفارشات فیلتر شده بر اساس نقش کارمند.
        """
        # ===== چک کردن دسترسی ===== #
        AppPermissionChecker.check_has_permission(requester, 'view_order')
        # ===== نمایش سفارشات کلی براساس نقش ===== #
        queryset = self.repo.get_all_orders_summary()
        # ===== فیلترینگ براساس نقش ===== #
        if requester.is_superuser:
            return queryset
        
        # ===== بررسی وجود نقش برای کاربر ===== #
        user_role_rel = requester.user_role.select_related('role').first()
        if not user_role_rel:
            return Order.objects.none()
        
        # ===== دریافت نقش کاربر ===== #
        role = user_role_rel.role
        allowed_groups = role.allowed_status_groups
        
        if role.type == "admin":
            return queryset.filter(current_status__group__code__in=allowed_groups)

        final_queryset = queryset.filter(Q(current_status__group__code__in=allowed_groups))

        return final_queryset
