import logging
from typing import List

from rest_framework.exceptions import PermissionDenied, ValidationError
from django.utils.translation import gettext as _

from core.models import User, Order, OrderStatus, OrderItem
from core.domain.commerce.order import(
    OrderRepository, OrderStatusFlowDomainService,
    OrderItemRepository, OrderStatusRepository
)
from apps.permissions import AppPermissionChecker

logger = logging.getLogger('apps.operations.transition')

# ========== Order Transition App Service ========== #
class OrderTransitionAppService:
    """
    سرویس اپلیکیشن ساده‌سازی شده برای مدیریت تغییر وضعیت سفارش.
    تمرکز فقط روی Order است.
    """
    def __init__(self):
        self.order_repo = OrderRepository()
        self.status_repo = OrderStatusRepository()
        self.flow_domain_service = OrderStatusFlowDomainService()
        
    def execute_transition(self, requester: User, new_status_code: str, order_id: int = None, order_item_id: int = None, description: str = None):
        """
        اجرای تغییر وضعیت دستی.
        مثال: طراح دکمه "اتمام طراحی" را می‌زند -> وضعیت به "آماده چاپ" می‌رود.
        """
        
        # ===== بررسی مجوز برای تغییر وضعیت ===== #
        logger.info(f"Transition request for Order #{order_id} to '{new_status_code}' by {requester.username}")
        AppPermissionChecker.check_has_permission(requester, 'change_orderstatus')
        
        # ===== دریافت سفارش مورد نظر ===== #
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise ValidationError("سفارش مورد نظر یافت نشد.")
        
        new_status = self.status_repo.get_status_by_code(new_status_code)
        if not new_status:
            raise ValidationError(f"کد وضعیت نامعتبر است: {new_status_code}")
        
        self._validate_role_scope(requester, order.current_status)
        self._validate_transition_direction(order.current_status, new_status)
        
        updated_order = self.flow_domain_service.change_order_status(
            order=order,
            new_status_code=new_status.internal_code,
            user=requester,
            description=description
        )
        
        return updated_order
    
    # ===== افزودن آیتم به سفارش ===== #
    def _handle_item_transition(self, user: User, item_id: int, new_status: OrderStatus, description: str):
        """
        مخصوص طراح، چاپچی و QC.
        """
        # الف) دریافت آیتم
        item = self.item_repo.model.objects.select_related('order', 'status__group', 'product').prefetch_related('files').filter(id=item_id).first()
        if not item:
            raise ValidationError("آیتم سفارش یافت نشد.")
        self._validate_item_permission(user, item, new_status)

        # ج) اعتبارسنجی جهت حرکت (جلوگیری از عقبگرد غیرمجاز)
        self._validate_transition_direction(item.status, new_status)

        # د) اعتبارسنجی فایل‌ها (فقط اگر داریم تایید طراحی می‌کنیم)
        if new_status.group.code == 'design' and new_status.status_type == 'approve':
            self._validate_item_files(item)

        # هـ) فراخوانی سرویس دامین (که لاجیک Rollup را هم صدا می‌زند)
        updated_item = self.flow_domain_service.change_item_status(
            item_id=item.id,
            new_status_code=new_status.internal_code,
            user=user,
            description=description
        )
        
        if new_status.status_type == 'reject' and item.assigned_to:
             item.assigned_to = None
             item.save(update_fields=['assigned_to'])

        return updated_item
    
    # ===== بررسی مجوز آیتم ===== #
    def _handle_order_transition(self, user: User, order_id: int, new_status: OrderStatus, description: str):
        """
        مخصوص مالی، انبار و ادمین.
        """
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise ValidationError("سفارش یافت نشد.")

        # بررسی دسترسی روی وضعیت فعلی سفارش
        self._validate_role_scope(user, order.current_status)

        # اعتبارسنجی جهت حرکت
        self._validate_transition_direction(order.current_status, new_status)

        # فراخوانی سرویس دامین
        return self.flow_domain_service.change_order_status(
            order=order,
            new_status_code=new_status.internal_code,
            user=user,
            description=description
        )
        
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
        if user.is_superuser or not current_status:
            return

        user_role_rel = user.user_role.select_related('role').first()
        if not user_role_rel:
            raise PermissionDenied("کاربر فاقد نقش سیستمی است.")
            
        role = user_role_rel.role

        if getattr(role, 'is_admin', False) or getattr(role, 'can_view_all_orders', False):
            return

        # # ===== بررسی دسترسی به تغییر وضعیت سفارش ===== #
        if current_status.group.code not in role.allowed_status_groups:
            raise PermissionDenied(f"شما دسترسی به تغییر سفارش در مرحله '{current_status.group.name}' را ندارید.")

    def _validate_item_files(self, item: OrderItem):
        """
        فیکس باگ نسخه قبلی:
        اینجا فقط فایل‌های همین آیتم (item.files) چک می‌شود نه فایل‌های کل سفارش.
        """
        product = item.product
        required_specs = product.file_upload_requirements.filter(is_required=True)
        
        if not required_specs.exists():
            return

        # دریافت فایل‌های تایید شده یا در انتظار همین آیتم
        # نکته: اگر وضعیت جدید Approve است، فایل‌ها باید حتما Approved باشند (توسط QC) یا حداقل موجود باشند.
        uploaded_files = item.files.filter(is_latest=True).exclude(status='rejected')
        uploaded_req_ids = set(f.requirement_id for f in uploaded_files)
        
        missing = []
        for req in required_specs:
            if req.id not in uploaded_req_ids:
                missing.append(req.spec.name)
        
        if missing:
             raise ValidationError(f"فایل‌های الزامی برای این آیتم آپلود نشده‌اند: {', '.join(missing)}")
        
        # چک سخت‌گیرانه: اگر سیستم QC دارید، همه فایل‌ها باید سبز (Approved) باشند
        for f in uploaded_files:
            if f.status != 'approved':
                raise ValidationError(f"فایل '{f.filename}' هنوز توسط واحد کنترل کیفیت تایید نشده است.")

    def _validate_transition_direction(self, current_status: OrderStatus, new_status: OrderStatus):
        """
        قانون حرکت: دنده عقب فقط با وضعیت 'رد شده' (Reject) مجاز است.
        """
        if not current_status:
            return
            
        if current_status.id == new_status.id:
            return

        is_backward = new_status.sort_order < current_status.sort_order
        if is_backward and new_status.status_type != 'reject':
             raise ValidationError(f"بازگشت به عقب ({new_status.name}) فقط در صورت 'رد کردن' سفارش مجاز است.")