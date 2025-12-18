from rest_framework.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _

from core.domain.infrastructure.logger.services import AuditLogDomainService
from core.domain.commerce.order import OrderRepository
from core.models import User

# ========== Order Detail App Service ========== # 
class OrderDetailAppService:
    """
    سرویس اپلیکیشن برای دیدن جزئیات کامل یک سفارش براساس نقش
    """
    def __init__(self):
        self.repo = OrderRepository()
        self.audit_service = AuditLogDomainService()

    def get_order_detail(self, requester: User, order_id: int):
        """
        مشاهده جزئیات براساس نقش و مجوزهای دسترسی
        """
        # ===== دریافت جزئیات کامل سفارش (از کوئری ریپازیتوری قبلاً اصلاح شده) ===== #
        order = self.repo.get_full_order_detail_for_admin(order_id)
        if not order:
            raise ValueError("سفارش یافت نشد.")
        
        try:
            # ===== دریافت نقش کاربر و چک‌های اولیه ===== #
            if requester.is_superuser:
                self._log_access(requester, order, 'superuser', 'granted')
                return order, 'superuser'
            
            user_role_rel = requester.user_role.select_related('role').first()
            if not user_role_rel:
                raise PermissionDenied("شما نقشی ندارید.")
            
            role = user_role_rel.role
             
            # ===== بررسی وجود گروه وضعیتی ===== #
            allowed_group_codes = [g.code for g in role.allowed_groups.all()]
            
            if not allowed_group_codes:
                 raise PermissionDenied("گروه وضعیتی برای شما تعریف نشده است.")
             
            # ===== بررسی دسترسی ===== #
            current_group_code = order.current_status.group.code
            if current_group_code not in allowed_group_codes:
                 raise PermissionDenied(f"شما دسترسی به مشاهده سفارش در مرحله '{order.current_status.group.name}' را ندارید.")
             
            # ===== لاگ دسترسی موفق ===== #
            self._log_access(requester, order, role.slug, 'granted')
            
            return order, role.slug

        except PermissionDenied as e:
            # ===== لاگ دسترسی ناموفق ===== #
            self._log_access(requester, order, 'unknown', 'denied', str(e))
            raise e
        
    def _log_access(self, user, order, role, status, reason=None):
        """ متد کمکی برای لاگ دسترسی خواندن """
        self.audit_service.record_log(
            user=user,
            obj=order,
            action='VIEW_ORDER_DETAIL',
            changes={'access_status': status, 'role_used': role, 'denial_reason': reason},
            description=_("مشاهده جزئیات سفارش")
        )