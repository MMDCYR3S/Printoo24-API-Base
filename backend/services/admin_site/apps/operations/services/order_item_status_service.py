import logging
from datetime import datetime

from rest_framework.exceptions import PermissionDenied, ValidationError
from django.utils.translation import gettext as _

from core.models import User, OrderItem
from core.domain.commerce.order import OrderItemRepository
from core.domain.infrastructure.logger.services import AuditLogDomainService
from apps.permissions import AppPermissionChecker

# ========== Logger ========== #
logger = logging.getLogger('apps.operations.item_status')

# ========== Order Item Status Service ========= #
class OrderItemStatusAppService:
    """
    سرویس مدیریت وضعیت فنی آیتم‌های سفارش (OrderItem Status).
    """
    def __init__(self):
        self.item_repo = OrderItemRepository()
        self.audit_service = AuditLogDomainService()

    def change_item_status(self, requester: User, item_id: int, new_status: str, admin_note: str = None):
        """
        تغییر وضعیت آیتم توسط پرسنل (طراح/چاپخانه).
        """
        # ===== بررسی دسترسی ===== #
        AppPermissionChecker.check_has_permission(requester, 'change_orderitem')
        
        # ===== دریافت آیتم ===== #
        item = self.item_repo.get_by_id(item_id)
        if not item:
            raise ValidationError(_("آیتم سفارش یافت نشد."))
        
        # ===== چک کردن اجازه دسترسی ===== #
        self._validate_access(requester, item)
        
        # ===== اعتبارسنجی تغییر وضعیت ===== #
        valid_statuses = dict(OrderItem.STATUS_CHOICES).keys()
        if new_status not in valid_statuses:
            raise ValidationError(f"وضعیت '{new_status}' نامعتبر است.")
        
        # ===== تغییر وضعیت ===== #
        old_status = item.status
        item.status = new_status

        # ===== افزودن یادداشت ===== #
        if admin_note:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            new_note = f"[{timestamp} - {requester.username}]: {admin_note}"
            if item.admin_note:
                item.admin_note += f"\n{new_note}"
            else:
                item.admin_note = new_note
        
        item.save(update_fields=['status', 'admin_note', 'updated_at'])
        
        logger.info(f"Item #{item.id} status changed: {old_status} -> {new_status} by {requester.username}")
        
        # ===== ثبت لاگ سیستماتیک ===== #
        self.audit_service.record_log(
            user=requester,
            obj=item,
            action='ITEM_STATUS_CHANGE',
            changes={
                'from': old_status,
                'to': new_status,
                'note_added': bool(admin_note),
                'note_snippet': admin_note[:50] if admin_note else None
            },
            description=_(f"تغییر وضعیت آیتم سفارش به {new_status}")
        )
        
        return item
    
    # ========== VALIDATORS ========== #
    def _validate_access(self, user: User, item: OrderItem):
        """
        بررسی اینکه آیا کاربر اجازه تغییر وضعیت این آیتم خاص را دارد؟
        """
        if user.is_superuser:
            return
        
        # ===== چک کردن نقش کاربر ===== #
        user_role_rel = user.user_role.select_related('role').first()
        if not user_role_rel:
            raise PermissionDenied("کاربر فاقد نقش سیستمی است.")
        
        role = user_role_rel.role
        
        order_group_code = item.order.current_status.group.code
        if order_group_code not in role.allowed_status_groups:
            self.audit_service.record_log(
                user=user,
                obj=item,
                action='ITEM_ACCESS_DENIED',
                changes={'current_stage': order_group_code, 'user_role': role.slug},
                description=_("تلاش غیرمجاز برای تغییر آیتم در مرحله غیرمرتبط")
            )
            raise PermissionDenied("شما در این مرحله از سفارش اجازه تغییر آیتم را ندارید.")
