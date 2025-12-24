from rest_framework.exceptions import PermissionDenied, NotFound
from django.utils.translation import gettext_lazy as _

from core.models import User, Order
from core.logger.services import LoggerService

# ========== Order Detail App Service ========== # 
class OrderDetailAppService:
    """
    سرویس اپلیکیشن برای دیدن جزئیات کامل یک سفارش براساس نقش
    """
    def __init__(self):
        self.audit_service = LoggerService()

    def get_order_detail(self, requester: User, order_id: int):
        """
        مشاهده جزئیات براساس نقش و مجوزهای دسترسی.
        خروجی: (Order Object, Role Slug)
        """
        # ===== دریافت سفارش ===== #
        order = Order.objects.get_full_order_detail_for_admin(order_id)
        
        if not order:
            raise NotFound("سفارش مورد نظر یافت نشد.")
        
        try:
            # ===== دریافت نقش کاربر و چک‌های اولیه ===== #
            if requester.is_superuser:
                self._log_access(requester, order, 'superuser', 'granted')
                return order, 'superuser'
            # ===== بررسی نقش ===== #
            user_role_rel = requester.user_role.select_related('role').first()
            if not user_role_rel:
                raise PermissionDenied("شما هیچ نقش سیستمی فعالی ندارید.")
            
            role = user_role_rel.role
             
            # ===== بررسی وجود گروه وضعیتی ===== #
            allowed_group_codes = list(role.allowed_groups.values_list('code', flat=True))
            if not allowed_group_codes:
                 raise PermissionDenied(f"نقش '{role.name}' دسترسی به هیچ مرحله‌ای از سفارشات را ندارد.")
             
            # ===== بررسی دسترسی ===== #
            if not order.current_status or not order.current_status.group:
                 raise PermissionDenied(f"شما دسترسی به مشاهده سفارش در مرحله '{order.current_status.group.name}' را ندارید.")
             
            current_group_code = order.current_status.group.code
            if current_group_code not in allowed_group_codes:
                raise PermissionDenied(
                    f"نقش شما ({role.name}) اجازه مشاهده سفارش در مرحله '{order.current_status.group.name}' را ندارد."
                )
            # ===== 5. لاگ دسترسی موفق ===== #
            self._log_access(requester, order, role.slug, 'granted')
            return order, role.slug

        except PermissionDenied as e:
            # ===== لاگ دسترسی ناموفق ===== #
            self._log_access(requester, order, 'unknown', 'denied', str(e))
            raise e
    
    # ========== LOG ACCESS ========== #
    def _log_access(self, user, order, role, status, reason=None):
        """ متد کمکی برای ثبت لاگ دسترسی خواندن """
        changes = {
            'access_status': status, 
            'role_used': role,
            'order_code': order.order_code,
            'current_status': order.current_status.name if order.current_status else 'None'
        }
        
        if reason:
            changes['denial_reason'] = reason

        self.audit_service.record_log(
            user=user,
            obj=order,
            action='VIEW_ORDER_DETAIL',
            changes=changes,
            description=_("مشاهده جزئیات کامل سفارش")
        )