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

    # ===== EXECUTE APPROVE ===== #    
    def execute_approve(self, requester: User, order_id: int, description: str = None):
        """
        تایید و جلو بردن وضعیت سفارش به مرحله بعد (Next Status).
        
        لاجیک عملکرد:
        1. بررسی دسترسی کاربر به گروه وضعیت فعلی (Group Access).
        2. پیدا کردن وضعیت بعدی بر اساس sort_order.
        3. اعمال تغییر وضعیت.
        """

        # ===== بررسی مجوز کاربر ===== #
        AppPermissionChecker.check_has_permission(requester, 'change_orderstatus')
        
        # ===== تلاش برای دریافت سفارش ===== #
        try:
            order = Order.objects.get_order_by_id(order_id)
            if not order:
                raise ValidationError("سفارش یافت نشد.")
        except Exception:
            raise ValidationError("خطا در بازیابی سفارش.")

        # ===== در صورت نبود وضعیت برای سفارش ===== #
        current_status = order.current_status
        if not current_status:
            raise ValidationError("این سفارش هنوز وضعیتی ندارد.")

        try:
            # ===== بررسی دسترسی به وضعیت ===== #
            self._validate_role_scope(requester, current_status)
            next_sort_order = current_status.sort_order + 1

            # ===== بررسی وجود وضعیت بعدی ===== #
            try:
                next_status = OrderStatus.objects.filter(sort_order=next_sort_order).first()
            except Exception:
                next_status = None

            if not next_status:
                raise ValidationError("این سفارش در مرحله نهایی قرار دارد و وضعیت بعدی برای تایید وجود ندارد.")

            # ===== مراحلی که نباید تغییر کنند ===== #
            FORBIDDEN_TRANSITIONS = ['deliver', 'cancel', 'reject']

            target_code = next_status.internal_code.lower()

            if any(keyword in target_code for keyword in FORBIDDEN_TRANSITIONS):
                raise ValidationError(
                    "برای انتقال به این مرحله (تکمیل/تحویل)، لطفا از دکمه مربوطه اقدام کنید. "
                    "تایید خودکار برای مراحل نهایی مجاز نیست."
                )

            
            # ===== تغییر وضعیت ===== #
            return self.flow_domain_service.change_order_status(
                order=order,
                new_status_code=next_status.internal_code,
                user=requester,
                description=description or _(f"تایید و انتقال خودکار به {next_status.name}")
            )

        except (ValidationError, PermissionDenied) as e:
            # ===== ثبت لاگ خطا ===== #
            self.audit_service.record_log(
                user=requester,
                obj=order,
                action='APPROVE_FAILED',
                changes={
                    'from': current_status.internal_code,
                    'attempt': 'NEXT_STATUS',
                    'error_type': type(e).__name__,
                    'error_message': str(e)
                },
                description=_(f"تلاش ناموفق برای تایید سفارش")
            )
            raise e


    # ===== EXECUTE TRANSITION ===== #
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
        
    # ===== VALIDATE ITEM PERMISSION / ACTION ===== #
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
        
    # ===== VALIDATE ROLE SCOPE / ACTION ===== #
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
    
    # ===== VALIDATE TRANSITION DIRECTION / ACTION ===== #
    def _validate_transition_direction(self, current_status: OrderStatus, new_status: OrderStatus):
        """
        قانون حرکت: دنده عقب فقط با وضعیت 'رد شده' (Reject) مجاز است.
        """
        if not current_status:
            return

        if current_status.id == new_status.id:
            return

        is_backward = new_status.sort_order < current_status.sort_order

    # ===== VALIDATE ALL ORDER FILES / ACTION ===== #
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
