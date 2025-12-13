from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from typing import Dict, Any

from core.models import Order, User, OrderStatusGroup, OrderStatus, OrderItem
from .repositories import (
    StatusFlowRepository,
    OrderStatusGroupRepository,
    OrderStatusRepository,
)
from core.domain.commerce.order import OrderItemRepository
from core.domain.commerce.order.exceptions import OrderNotFoundException

class OrderStatusFlowDomainService:
    """
    سرویس مدیریت وضعیت سفارش (Workflow Engine).
    مسئول تضمین صحت تغییر وضعیت و ثبت تاریخچه است.
    """
    def __init__(self):
        self.repo = StatusFlowRepository()
        self.item_repo = OrderItemRepository()
        self.status_repo = OrderStatusRepository()
        
    @transaction.atomic
    def change_order_status(self, order: Order, new_status_code: str, user: User, description: str = None) -> Order:
        """
        تغییر وضعیت دستی سفارش (مثلاً برای مراحل مالی یا ارسال).
        """
        if not order:
            raise OrderNotFoundException("سفارش یافت نشد.")
        
        new_status = self.repo.get_status_by_code(new_status_code)
        if not new_status:
            raise ValidationError(f"کد وضعیت نامعتبر: {new_status_code}")

        # اگر وضعیت جدید مربوط به "آیتم" باشد، نباید روی "سفارش" ست شود
        if new_status.target_model == 'item':
             raise ValidationError("این وضعیت مختص اقلام سفارش است و نمی‌تواند روی کل سفارش اعمال شود.")

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

        # ثبت لاگ آیتم (باید مدل لاگ آیتم داشته باشی یا از همون لاگ سفارش با فیلد item استفاده کنی)
        # self.repo.create_item_state_log(...) 
        
        item.status = new_status
        item.save(update_fields=['status', 'updated_at'])

        # 2. فراخوانی منطق تجمیع (Rollup) برای آپدیت سفارش مادر
        self._update_master_order_status(item.order, user)

        return item
    
    # ================================================= #
    # ============ منطق هسته (Core Logic) ============ #
    # ================================================= #
    def _perform_transition(self, order: Order, new_status: OrderStatus, user: User, description: str = None):
        """ متد کمکی برای جلوگیری از تکرار کد در تغییر وضعیت سفارش """
        old_status = order.current_status
        
        if old_status and old_status.internal_code == new_status.internal_code:
            return order
        
        # محاسبه مدت زمان
        last_log = self.repo.get_last_state_log(order)
        duration = timezone.now() - last_log.timestamp if last_log else None
        
        # ثبت لاگ
        self.repo.create_state_log({
            "order": order,
            "from_status": old_status,
            "to_status": new_status,
            "user": user,
            "description": description,
            "duration_in_previous_status": duration
        })

        # آپدیت
        order.current_status = new_status
        order.save(update_fields=['current_status', 'updated_at'])
        return order

    def _update_master_order_status(self, order: Order, user: User):
        """
        همون Rollup Logic معروف!
        بررسی می‌کند وضعیت آیتم‌ها چیست و وضعیت سفارش را بر اساس آن تنظیم می‌کند.
        """
        items = order.order_item_order.all() # فرض بر اینکه related_name='order_item_order' است
        total_items = items.count()

        if total_items == 0:
            return

        # 1. اگر حتی یک آیتم رد شده باشد -> وضعیت سفارش: بررسی لازم (Attention)
        if items.filter(status__status_type='reject').exists():
            target_code = 'ATTENTION_NEEDED' # باید در دیتابیس تعریف شده باشد
        
        # 2. اگر همه تکمیل شده‌اند -> وضعیت سفارش: تکمیل شده (Completed)
        elif items.filter(status__internal_code='DELIVERED').count() == total_items:
            target_code = 'COMPLETED'
            
        # 3. اگر همه در حال چاپ هستند (یا جلوتر) -> وضعیت سفارش: در حال پردازش
        elif items.filter(status__group__code='production').count() == total_items:
             target_code = 'IN_PRODUCTION'
             
        else:
            # هیچ کاری نکن یا وضعیت پیش‌فرض بذار
            return 

        # دریافت آبجکت وضعیت
        new_master_status = self.status_repo.get_status_by_code(target_code)
        
        # اگر وضعیت جدید با فعلی فرق دارد، سفارش را آپدیت کن
        if new_master_status and order.current_status != new_master_status:
            self._perform_transition(
                order=order, 
                new_status=new_master_status, 
                user=user, 
                description="تغییر وضعیت اتوماتیک بر اساس پیشرفت آیتم‌ها"
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
