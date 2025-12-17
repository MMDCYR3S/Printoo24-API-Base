from typing import Dict, Any

from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from core.models import Order, User, OrderStatusGroup, OrderStatus, OrderItem
from .repositories import (
    StatusFlowRepository,
    OrderStatusGroupRepository,
    OrderStatusRepository,
)
from core.domain.commerce.order import OrderItemRepository
from core.domain.commerce.order.exceptions import OrderNotFoundException
from core.domain.infrastructure.logger import AuditLogDomainService


# ========== Order Status Flow Service ========== #
class OrderStatusFlowDomainService:
    """
    سرویس مدیریت وضعیت سفارش (Workflow Engine).
    مسئول تضمین صحت تغییر وضعیت و ثبت تاریخچه است.
    """
    def __init__(self):
        self.repo = StatusFlowRepository()
        self.item_repo = OrderItemRepository()
        self.status_repo = OrderStatusRepository()
        self.audit_service = AuditLogDomainService()
        
    @transaction.atomic
    def change_order_status(self, order: Order, new_status_code: str, user: User, description: str = None) -> Order:
        """
        تغییر وضعیت سفارش توسط کاربر یا سیستم.
        """
        # ===== بررسی اینکه آیا وضعیت جدید معتبر است ===== #
        new_status = self.repo.get_status_by_code(new_status_code)
        if not new_status:
            raise ValidationError(f"کد وضعیت نامعتبر: {new_status_code}")
        # ===== جلوگیری از تکرار ===== #
        if order.current_status_id == new_status.id:
            return order
        # ===== اجرای تغییر وضعیت ===== #
        return self._perform_transition(order, new_status, user, description)

    @transaction.atomic
    def change_item_status(self, item_id: int, new_status_code: str, user: User, description: str = None) -> OrderItem:
        """
        تغییر وضعیت یک قلم کالا (مثلاً تایید طراحی کارت ویزیت).
        این متد اتوماتیک وضعیت سفارش مادر را هم آپدیت می‌کند.
        """
        item = self.item_repo.get_by_id(item_id)
        if not item:
            raise ValidationError("آیتم سفارش یافت نشد.")

        new_status = self.repo.get_status_by_code(new_status_code)
        if not new_status:
            raise ValidationError(f"کد وضعیت نامعتبر: {new_status_code}")
            
        if new_status.target_model == 'order':
             raise ValidationError("این وضعیت مختص کل سفارش است و نمی‌تواند روی آیتم اعمال شود.")

        # 1. تغییر وضعیت آیتم
        old_status = item.status
        if old_status and old_status.internal_code == new_status_code:
            return item

        changes = {
            "field": "status",
            "from_id": old_status.id if old_status else None,
            "to_id": new_status.id,
            "from_title": old_status.title if old_status else "N/A",
            "to_title": new_status.title,
            "internal_code_change": f"{old_status.internal_code if old_status else 'None'} -> {new_status.internal_code}"
        }

        self.audit_service.record_log(
            user=user,
            obj=item,
            action='STATUS_CHANGE',
            changes=changes,
            description=description or _("تغییر وضعیت آیتم سفارش")
        )
        
        item.status = new_status
        item.save(update_fields=['status', 'updated_at'])

        # 2. فراخوانی منطق تجمیع (Rollup) برای آپدیت سفارش مادر
        self._update_master_order_status(item.order, user)

        return item
    
    # ============ منطق هسته ============ #
    def _perform_transition(self, order: Order, new_status: OrderStatus, user: User, description: str = None):
        """ متد کمکی برای جلوگیری از تکرار کد در تغییر وضعیت سفارش """
        old_status = order.current_status
        
        # ===== محاسبه مدت زمان توقف در مرحله قبل ===== #
        last_log = self.audit_service.get_last_action_log(order, action='STATUS_CHANGE')
        
        duration_seconds = 0
        formatted_duration = "N/A"
        
        if last_log:
            delta = timezone.now() - last_log.timestamp
            duration_seconds = delta.total_seconds()
            formatted_duration = str(delta).split('.')[0]
        
        # ===== آماده‌سازی داده‌های لاگ ===== #
        changes_data = {
            "transition": "order_status_update",
            "from_status": {
                "id": old_status.id if old_status else None,
                "title": old_status.title if old_status else "آغاز فرایند",
                "code": old_status.internal_code if old_status else None
            },
            "to_status": {
                "id": new_status.id,
                "title": new_status.title,
                "code": new_status.internal_code
            },
            "metrics": {
                "duration_seconds": int(duration_seconds),
                "duration_readable": formatted_duration
            }
        }

        # ===== ثبت لاگ ===== #
        self.audit_service.record_log(
            user=user,
            obj=order,
            action='STATUS_CHANGE',
            changes=changes_data,
            description=description or _(f"تغییر وضعیت سفارش به {new_status.title}")
        )

        # ===== آپدیت نهایی دیتابیس ===== #
        order.current_status = new_status
        order.save(update_fields=['current_status', 'updated_at'])
        
        return order

    def _update_master_order_status(self, order: Order, user: User):
        """
        منطق تجمیع وضعیت آیتم‌ها (Rollup Logic).
        این بخش منطق بیزینس است و تغییری نکرده، اما حالا از متد _perform_transition جدید استفاده می‌کند.
        """
        items = order.order_item_order.all()
        total_items = items.count()

        if total_items == 0:
            return

        target_code = None
        
        # ===== رد شدن آیتم ===== #
        if items.filter(status__status_type='reject').exists():
            target_code = 'ATTENTION_NEEDED'
            
        # ===== تایید شدن آیتم ===== #
        elif items.filter(status__internal_code='DELIVERED').count() == total_items:
            target_code = 'COMPLETED'
            
        elif items.filter(status__group__code='production').count() == total_items:
            target_code = 'IN_PRODUCTION'
        
        if not target_code:
            return

        new_master_status = self.status_repo.get_status_by_code(target_code)
        
        if new_master_status and order.current_status_id != new_master_status.id:
            self._perform_transition(
                order=order, 
                new_status=new_master_status, 
                user=user,
                description="بروزرسانی خودکار بر اساس وضعیت آیتم‌ها"
            )

# ===== Order Status Group Domain Service ===== #
class OrderStatusGroupDomainService:
    """
    سرویس دامنه برای مدیریت گروه‌های وضعیت (OrderStatusGroup).
    """
    def __init__(self):
        self.repo = OrderStatusGroupRepository()

    @transaction.atomic
    def create_group(self, data: Dict[str, Any]) -> OrderStatusGroup:
        """ ایجاد گروه وضعیت جدید. """
        code = data.get('code')
        if self.repo.get_group_by_code(code):
            raise ValidationError(f"گروه با کد سیستمی '{code}' قبلاً وجود دارد.")
        
        return self.repo.create(data)

    @transaction.atomic
    def update_group(self, group_id: int, data: Dict[str, Any]) -> OrderStatusGroup:
        """ ویرایش گروه وضعیت. """
        group = self.repo.get_by_id(group_id)
        if not group:
            raise ValidationError("گروه وضعیت یافت نشد.")

        code = data.get('code')
        if code and code != group.code and self.repo.get_group_by_code(code):
            raise ValidationError(f"کد سیستمی '{code}' تکراری است.")

        return self.repo.update(group, data)

    def delete_group(self, group_id: int):
        """ حذف گروه وضعیت با بررسی وابستگی. """
        group = self.repo.get_by_id(group_id)
        if not group:
            raise ValidationError("گروه وضعیت یافت نشد.")

        if group.order_status.exists():
            raise ValidationError("امکان حذف نیست. این گروه وضعیت به یک یا چند وضعیت سفارش متصل است.")
        group.delete()

# ========== Order Status Domain Service ========== #
class OrderStatusDomainService:
    """
    سرویس دامنه برای مدیریت وضعیت‌های سفارش (Status CRUD).
    """
    def __init__(self):
        self.repo = OrderStatusRepository()

    @transaction.atomic
    def create_status(self, data: Dict[str, Any]) -> OrderStatus:
        """ ایجاد وضعیت جدید. """
        code = data.get('internal_code')
        if self.repo.get_status_by_code(code):
            raise ValidationError(f"کد سیستمی وضعیت '{code}' قبلاً وجود دارد.")
        
        return self.repo.create(data)

    @transaction.atomic
    def update_status(self, status_id: int, data: Dict[str, Any]) -> OrderStatus:
        """ ویرایش وضعیت. """
        status_obj = self.repo.get_by_id(status_id)
        if not status_obj:
            raise ValidationError("وضعیت یافت نشد.")

        code = data.get('internal_code')
        if code and code != status_obj.internal_code and self.repo.get_status_by_code(code):
            raise ValidationError(f"کد سیستمی '{code}' تکراری است.")

        return self.repo.update(status_obj, data)

    def delete_status(self, status_id: int):
        """ حذف وضعیت با بررسی وابستگی به Orders. """
        status_obj = self.repo.get_status_with_group_detail(status_id)
        if not status_obj:
            raise ValidationError("وضعیت یافت نشد.")
            
        if self.repo.check_for_active_orders(status_obj):
            raise ValidationError("امکان حذف نیست. حداقل یک سفارش فعال از این وضعیت استفاده می‌کند.")
            
        status_obj.delete()
