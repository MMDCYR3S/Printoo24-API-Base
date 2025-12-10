import logging
from typing import List

from rest_framework.exceptions import PermissionDenied, ValidationError

from core.models import User, Order, OrderStatus
from core.domain.commerce.order import(
    OrderRepository, OrderStatusFlowDomainService,
    OrderItemRepository, OrderStatusRepository
)
from apps.permissions import AppPermissionChecker

logger = logging.getLogger('apps.operations.transition')

# ========== Order Transition App Service ========== #
class OrderTransitionAppService:
    """
    سرویس اپلیکیشن برای مدیریت تغییر وضعیت دستی سفارشات توسط پرسنل.
    وظیفه اصلی: بررسی Access Scope کاربر قبل از تغییر وضعیت.
    """
    def __init__(self):
        self.order_repo = OrderRepository()
        self.item_repo = OrderItemRepository()
        self.status_repo = OrderStatusRepository()
        self.flow_domain_service = OrderStatusFlowDomainService()
        
    def execute_transition(self, requester: User, order_id: int, new_status_code: str, description: str = None):
        """
        اجرای تغییر وضعیت دستی.
        مثال: طراح دکمه "اتمام طراحی" را می‌زند -> وضعیت به "آماده چاپ" می‌رود.
        """
        
        # ===== بررسی مجوز برای تغییر وضعیت ===== #
        logger.info(f"Transition request for Order {order_id} to '{new_status_code}' by {requester.username}")
        AppPermissionChecker.check_has_permission(requester, 'change_orderstatus')
        
        # ===== دریافت سفارش مورد نظر ===== #
        order = self.order_repo.model.objects.select_related('current_status__group').prefetch_related(
            'order_item_order__files',
            'order_item_order__product__file_upload_requirements'
        ).filter(id=order_id).first()
        if not order:
            raise ValidationError("سفارش مورد نظر یافت نشد.")
        
        # ===== دریافت وضعیت جدید ===== #
        new_status = self.status_repo.get_status_by_code(new_status_code)
        if not new_status:
            raise ValidationError(f"کد وضعیت نامعتبر است: {new_status_code}")
        
        # ===== چک کردن وضعیت ===== #
        self._validate_transition_direction(order.current_status, new_status)        
        
        # ===== بررسی دسترسی نقش کاربر ===== #
        if not requester.is_superuser:
            role = self._validate_role_scope(requester, order)
            self._validate_assignment(requester, order, role)
            
        # ===== بررسی ارسال و تایید فایل های طراحی ===== #
        self._validate_design_files(order)
        # ===== بررسی وضعیت هر فایل ===== #
        self._validate_file_status(order)
        
        
        # ===== فراخوانی سرویس دامنه برای تغییر وضعیت اتمیک ===== #
        updated_order = self.flow_domain_service.change_order_status(
            order=order,
            new_status_code=new_status_code,
            user=requester,
            description=description
        )
        
        # ===== اگر هنوز به طراح اختصاص داده شده بود، assigned_to رو برابر هیچی قرار میدیم ===== #
        if order.order_item_order.filter(assigned_to__isnull=False).exists():
            order_items = self.item_repo.filter(order=order)
            for item in order_items:
                item.assigned_to = None
                item.save(update_fields=['assigned_to', 'updated_at'])

        return updated_order
        
    def _validate_role_scope(self, user: User, order: Order):
        """
        بررسی می‌کند که آیا سفارش در مرحله‌ای است که کاربر به آن دسترسی دارد؟
        """
        # ===== دریافت نقش کاربر ===== #
        user_role_rel = user.user_role.select_related('role').first()
        if not user_role_rel:
            raise PermissionDenied("شما هیچ نقش فعالی در سیستم ندارید.")
        
        role = user_role_rel.role
        
        # ===== بررسی دسترسی ابر کاربر ===== #
        if getattr(role, 'is_admin', False):
            return
        
        # ===== دریافت کد گروه وضعیت ===== #
        current_status = order.current_status
        if not current_status or not current_status.group:
            raise PermissionDenied("وضعیت فعلی سفارش نامعتبر است.")
        
        current_group_code = current_status.group.code
        
        # ===== بررسی وجود کد وضعیت در دسترسی‌های نقش ===== #
        if current_group_code not in role.allowed_status_groups:
            raise PermissionDenied(
                f"شما اجازه تغییر وضعیت سفارش در مرحله '{current_status.group.name}' را ندارید."
            )
            
        return role
        
    def _validate_assignment(self, user: User, order: Order, role):
        """
        بررسی مالکیت:
        برخی نقش‌ها (مثل طراح و چاپ) فقط باید روی سفارشاتی کار کنند که به آن‌ها Assign شده است.
        برخی نقش‌ها (مثل انبار یا مالی) ممکن است روی کل استخر سفارشات (Pool) کار کنند.
        """
        STRICT_ASSIGNMENT_ROLES = ['designer']
        
        if role.slug in STRICT_ASSIGNMENT_ROLES:
            is_assigned = order.order_item_order.filter(assigned_to=user).exists()
            if not is_assigned:
                raise PermissionDenied("این سفارش به شما اختصاص داده نشده است و نمی‌توانید وضعیت آن را تغییر دهید.")
    
    def _validate_design_files(self, order: Order):
        """
        بررسی می‌کند آیا تمام فایل‌های مورد نیاز (Required) آپلود شده‌اند؟
        """
        order_item = order.order_item_order.first()
        if not order_item:
            return
        
        product = order_item.product
        # ===== دریافت نیازمندی های محصول ===== #
        required_specs = product.file_upload_requirements.filter(is_required=True)
        if not required_specs.exists():
            return
    
        # ===== بررسی فایل های آپلود شده ===== #
        uploaded_files = order_item.files.filter(is_latest=True).exclude(status='rejected')
        uploaded_requirement_ids = set(f.requirement_id for f in uploaded_files)
        
        # ===== بررسی وجود تمام فایل‌های مورد نیاز ===== #
        missing_requirements = []
        for req in required_specs:
            if req.id not in uploaded_requirement_ids:
                missing_requirements.append(req.spec.name)
        # ===== در صورت وجود مغایرت، خطا دهد ===== #
        if missing_requirements:
            raise ValidationError(
                f"برای تغییر وضعیت، باید فایل‌های زیر را آپلود کنید: {', '.join(missing_requirements)}"
            )
    
    def _validate_file_status(self, order: Order):
        """
        اعتبارسنجی وضعیت هر فایل:
        اگر فایل آپلود شد و وضعیت آن تایید نبود، خطا دهد.
        """
        uploaded_files = order.order_item_order.first().files.filter(is_latest=True).exclude(status='rejected')
        for file in uploaded_files:
            if file.status != 'approved':
                raise ValidationError(
                    f"فایل '{file.file.name}' وضعیت '{file.get_status_display()}' دارد و نمی‌تواند تایید شود."
                )
        
    def _validate_transition_direction(self, current_status: OrderStatus, new_status: OrderStatus):
        """
        🚨 قانون حرکت وضعیت:
        کاربر می‌تواند به جلو حرکت کند.
        کاربر تنها زمانی می‌تواند به عقب (ترتیب کمتر) برگردد که نوع وضعیت جدید 'reject' باشد.
        """
        if not current_status:
            return
        
        is_backward_move = new_status.sort_order < current_status.sort_order
        
        # ===== بررسی برگشت وضعیت به عقب(فقط در صورتی که نوع 'رد شده' باشد) ===== #
        if is_backward_move:
            if new_status.status_type != 'reject':
                raise ValidationError(
                    f"نمی‌توانید سفارش را به مرحله قبل ({new_status.name}) برگردانید، مگر اینکه وضعیت از نوع 'رد شده' باشد."
                )
        # ===== بررسی تغییر وضعیت به وضعیت اولیه ===== #
        elif current_status.group_id != new_status.group_id:
            if new_status.status_type != 'initial':
                raise ValidationError(
                    f"ورود به گروه '{new_status.group.name}' فقط از طریق وضعیت آغازین آن امکان‌پذیر است."
                )
        