from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from typing import Dict, Any

from core.models import Order, User, OrderStatusGroup, OrderStatus
from .repositories import (
    StatusFlowRepository,
    OrderStatusGroupRepository,
    OrderStatusRepository
)
from core.domain.commerce.order.exceptions import OrderNotFoundException

class OrderStatusFlowDomainService:
    """
    سرویس مدیریت وضعیت سفارش (Workflow Engine).
    مسئول تضمین صحت تغییر وضعیت و ثبت تاریخچه است.
    """
    def __init__(self):
        self.repo = StatusFlowRepository()
        
    @transaction.atomic
    def change_order_status(self, order: Order, new_status_code: str, user: User, description: str = None) -> Order:
        """
        تغییر وضعیت سفارش به صورت اتمیک و ثبت لاگ.
        """
        if not order:
            raise OrderNotFoundException("سفارش یافت نشد.")
        
        # ===== دریافت وضعیت جدید ===== #
        new_status = self.repo.get_status_by_code(new_status_code)
        if not new_status:
            raise ValidationError(f"کد وضعیت نامعتبر: {new_status_code}")

        old_status = order.current_status
        
        # ===== جلوگیری از تغییرات تکراری ===== #
        if old_status and old_status.internal_code == new_status_code:
            return order
        
        # ===== محاسبه مدت زمان توقف در وضعیت قبلی ===== #
        last_log = self.repo.get_last_state_log(order)
        duration = timezone.now() - last_log.timestamp if last_log else None
        
        # ===== ثبت لاگ جدید ===== #
        self.repo.create_state_log({
            "order": order,
            "from_status": old_status,
            "to_status": new_status,
            "user": user,
            "description": description,
            "duration_in_previous_status": duration
        })

        # ===== آپدیت وضعیت ===== #
        order.current_status = new_status
        order.save(update_fields=['current_status', 'updated_at'])

        return order

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
