from typing import List
from django.db.models import Q

from core.domain.commerce.order.main import OrderRepository
from core.models import Order, User
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
        
        
        user_role_rel = requester.user_role.select_related('role').prefetch_related('role__scopes').first()
        if not user_role_rel:
            return Order.objects.none()
        
        # ===== دریافت نقش کاربر ===== #
        role = user_role_rel.role
        if not role:
            return queryset.none()
        
        if role.is_admin:
            allowed_groups = role.allowed_status_groups
            if not allowed_groups:
                return Order.objects.none()
            return self.repo.get_all_orders_summary().filter(
                current_status__group__code__in=allowed_groups
            )
            
        allowed_groups = role.allowed_status_groups
        if not allowed_groups:
            return Order.objects.none()
        
        scope_queryset = self.repo.get_all_orders_summary().filter(
            current_status__group__code__in=allowed_groups
        )
        
        return scope_queryset.filter(
            Q(order_item_order__assigned_to=requester) | 
            Q(order_item_order__assigned_to__isnull=True)
        ).distinct()