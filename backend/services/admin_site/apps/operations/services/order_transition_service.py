import logging
from typing import List

from rest_framework.exceptions import PermissionDenied, ValidationError
from django.utils.translation import gettext as _

from core.models import User, Order, OrderStatus, OrderItem
from apps.support.services import LoggerService
from apps.order.domain_services import OrderStatusFlowService
from apps.permissions import AppPermissionChecker

logger = logging.getLogger('apps.operations.transition')

# ========== Order Transition App Service ========== #
class OrderTransitionAppService:
    """
    سرویس اپلیکیشن ساده‌سازی شده برای مدیریت تغییر وضعیت سفارش (توسط دکمه‌های پنل).
    مسئولیت:
    1. چک کردن پرمیشن‌های اپلیکیشن.
    2. چک کردن لاجیک‌های امنیتی (Guard Logic) مثل دسترسی نقش به مرحله.
    3. فراخوانی سرویس دامین برای انجام تغییر وضعیت.
    """
    def __init__(self):
        self.flow_domain_service = OrderStatusFlowService()
        self.audit_service = LoggerService()
        
    def execute_transition(self, requester: User, new_status_code: str, order_id: int, description: str = None):
        """
        تغییر وضعیت سفارش.
        ورودی: فقط شناسه سفارش (چون آیتم وضعیت ندارد).
        """
        
       # ===== بررسی مجوز سطح دسترسی اپلیکیشن ===== #
        logger.info(f"Transition request for Order #{order_id} to '{new_status_code}' by {requester.username}")
        AppPermissionChecker.check_has_permission(requester, 'change_orderstatus')
        
        # ===== دریافت سفارش ===== #
        try:
            order = Order.objects.get_order_by_id(order_id)
            if not order:
                raise ValidationError("سفارش یافت نشد.")
        except Exception:
            raise ValidationError("خطا در بازیابی سفارش.")
        
        # ===== دریافت وضعیت جدید ===== #
        new_status = OrderStatus.objects.get_status_by_code(new_status_code)
        if not new_status:
            raise ValidationError(f"کد وضعیت نامعتبر است: {new_status_code}")
        
        try:
            # ===== اعتبارسنجی‌ها (Guards) ===== #
            self._validate_role_scope(requester, order.current_status)
            self._validate_transition_direction(order.current_status, new_status)
            self._validate_all_order_files(order)
            
            # ===== اجرای تغییر وضعیت (Delegation to Domain) ===== #
            return self.flow_domain_service.change_order_status(
                order=order,
                new_status_code=new_status.internal_code,
                user=requester,
                description=description
            )

        except (ValidationError, PermissionDenied) as e:
            # ===== لاگ شکست عملیات (بسیار مهم) ===== #
            self.audit_service.record_log(
                user=requester,
                obj=order,
                action='TRANSITION_FAILED',
                changes={
                    'from': order.current_status.internal_code if order.current_status else 'None',
                    'target': new_status_code,
                    'error_type': type(e).__name__,
                    'error_message': str(e)
                },
                description=_(f"تلاش ناموفق برای تغییر وضعیت سفارش")
            )
            raise e
        
    def _validate_item_permission(self, user: User, item: OrderItem, new_status: OrderStatus):
        """
        چک می‌کند آیا کاربر حق دارد به این آیتم دست بزند؟
        """
        if user.is_superuser:
            return

        user_role_rel = user.user_role.select_related('role').first()
        if not user_role_rel:
            raise PermissionDenied("کاربر فاقد نقش سیستمی است.")
        
        role = user_role_rel.role
        
        # ===== بررسی اینکه آیا وضعیت آیتم میتواند توسط نقش های مختلف تغییر پیدا کند یا خیر ===== #
        if getattr(role, 'can_view_all_orders', False):
            if not new_status.is_workflow_gate:
                raise PermissionDenied(
                    _("کنترل کیفی (QC) مجاز به انتقال وضعیت به این مرحله (%(status)s) نیست. این وضعیت یک دروازه فلو نیست.") % {'status': new_status.name}
                )
            if new_status.target_model != 'item':
                raise PermissionDenied(_("QC فقط مجاز به تغییر وضعیت‌های مربوط به اقلام سفارش (Item) است."))
            return

        if item.status and item.status.group.code not in role.allowed_status_groups:
             raise PermissionDenied(f"شما اجازه تغییر وضعیت آیتم در مرحله '{item.status.group.name}' را ندارید.")
        if role.is_task_based:
            if item.assigned_to and item.assigned_to != user:
                raise PermissionDenied(f"این آیتم توسط همکار شما ({item.assigned_to.username}) قفل شده است.")
        
    def _validate_role_scope(self, user: User, current_status: OrderStatus):
        """
        بررسی می‌کند آیا نقش کاربر اجازه دسترسی به سفارش در وضعیت فعلی را دارد؟
        """
        if user.is_superuser:
            return
        
        if not current_status:
            return

        user_role_rel = user.user_role.select_related('role').first()
        role = user_role_rel.role
        if role.type == 'admin':
            return
            
        # ===== بررسی اینکه آیا وضعیت گروه دسترسی برای کاربر هست یا خیر. اگر نه، نباید تغییر دهد ===== #
        if not role.allowed_groups.filter(id=current_status.group_id).exists():
             raise PermissionDenied(f"شما دسترسی به ویرایش سفارش در مرحله '{current_status.group.name}' را ندارید.")
         
    def _validate_transition_direction(self, current_status: OrderStatus, new_status: OrderStatus):
        """
        قانون حرکت: دنده عقب فقط با وضعیت 'رد شده' (Reject) مجاز است.
        """
        if not current_status:
            return

        if current_status.id == new_status.id:
            return

        is_backward = new_status.sort_order < current_status.sort_order

    def _validate_all_order_files(self, order: Order):
        """
        چک کردن فایل‌های تمام اقلام سفارش.
        اگر حتی یک آیتم فایل ناقص داشته باشد، کل سفارش نمی‌تواند جلو برود.
        """
        items = order.order_item_order.all()
        
        errors = []
        for item in items:
            product = item.product
            
            # ===== اگر آیتم تایید نشده بود، خطابده ===== #
            if not item.status == "approved":
                errors.append(f"آیتم باید تایید شود.")
                continue
            uploaded_files = item.files.filter(is_latest=True)

        if errors:
            raise ValidationError("\n".join(errors))

        return uploaded_files
