from typing import List
from django.db.models import Q

from core.domain.commerce.order.main import OrderRepository
from core.models import Order, User, OrderItem
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
        
        
        user_role_rel = requester.user_role.select_related('role').first()
        if not user_role_rel:
            return Order.objects.none()
        
        
        # ===== دریافت نقش کاربر ===== #
        role = user_role_rel.role
        allowed_groups = role.allowed_status_groups
        
        if getattr(role, 'can_view_all_orders', False):
            return queryset
        
        if role.is_admin:
            return queryset.filter(current_status__group__code__in=allowed_groups)
            
        item_filters = Q(status__group__code__in=allowed_groups)
        
        if role.is_task_based:
            assignment_filter = Q(assigned_to=requester) | Q(assigned_to__isnull=True)
            item_filters &= assignment_filter

        final_queryset = queryset.filter(order_item_order__in=OrderItem.objects.filter(item_filters)).distinct()

        return final_queryset