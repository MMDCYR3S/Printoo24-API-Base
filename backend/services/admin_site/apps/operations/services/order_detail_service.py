from rest_framework.exceptions import PermissionDenied, NotFound
from django.utils.translation import gettext_lazy as _
from django.db.models import Prefetch

from core.models import User, Order, OrderItem, OrderItemFile
from apps.order.models import OrderCostSheet, OrderCostReport, OrderCostItem
from apps.logistics.models import OrderShipment
from apps.support.services import LoggerService

# ========== Order Detail App Service ========== # 
class OrderDetailAppService:
    """
    سرویس اپلیکیشن برای دیدن جزئیات کامل یک سفارش براساس نقش
    """
    def __init__(self):
        self.audit_service = LoggerService()
        
    def _get_full_order_data(self, order_id: int):
        """
        متد خصوصی برای ساخت کوئری سنگین و دریافت سوپر-دیتا.
        این متد جایگزین متد منیجر قبلی می‌شود.
        """
        queryset = Order.objects.filter(id=order_id).select_related(
            'user', 
            'current_status__group', 
            'address__city',
            'address__province'
        ).prefetch_related(
            Prefetch(
                'order_item_order',
                queryset=OrderItem.objects.select_related('product').prefetch_related(
                    Prefetch(
                        'files', 
                        queryset=OrderItemFile.objects.filter(is_latest=True).order_by('-version')
                    )
                )
            )
        )
        return queryset.first()

    def get_order_detail(self, requester: User, order_id: int):
        """
        مشاهده جزئیات براساس نقش و مجوزهای دسترسی.
        خروجی: (Order Object, Role Slug)
        """
        # ===== دریافت سفارش ===== #
        order = self._get_full_order_data(order_id)
        if not order:
            raise NotFound("سفارش مورد نظر یافت نشد.")
        
        if requester.is_superuser:
            self._log_access(requester, order, 'superuser', 'granted')
            return order

        user_role_rel = requester.user_role.select_related('role').first()
        if not user_role_rel:
            raise PermissionDenied("شما هیچ نقش سیستمی فعالی ندارید.")
        
        role = user_role_rel.role
        allowed_group_codes = list(role.allowed_groups.values_list('code', flat=True))

        if role.type != 'admin':
            if not allowed_group_codes:
                 raise PermissionDenied(f"نقش '{role.name}' دسترسی به سفارشات را ندارد.")
            
            if not order.current_status or not order.current_status.group:
                 raise PermissionDenied("وضعیت سفارش نامعتبر است.")
             
            if order.current_status.group.code not in allowed_group_codes:
                raise PermissionDenied(f"دسترسی به این مرحله ({order.current_status.group.name}) ندارید.")

        self._log_access(requester, order, role.slug, 'granted')
        return order
    
    # ===== LOG ACCESS ===== #
    def _log_access(self, user, order, role, status, reason=None):
        changes = {
            'access_status': status, 
            'role_used': role,
            'order_code': order.order_code,
            'current_status': order.current_status.name if order.current_status else 'None'
        }
        if reason: changes['denial_reason'] = reason
        self.audit_service.record_log(
            user=user, obj=order, action='VIEW_ORDER_DETAIL', changes=changes, description="مشاهده جزئیات سفارش"
        )
