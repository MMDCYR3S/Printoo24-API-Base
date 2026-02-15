from typing import Dict, Any
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from apps.logistics.models import OrderShipment
from core.models import User, Order, OrderStatus
from apps.support.services import LoggerService

# ========== LOGISTIC SERVICE ========== #
class LogisticsService:
    """
    سرویس دامنه برای مدیریت منطق لجستیک، مرسوله‌ها و بسته‌بندی.
    """
    
    def __init__(self):
        self.audit_service = LoggerService()

    def validate_shipment_modification(self, shipment: OrderShipment):
        if shipment.status == 'delivered':
            raise ValidationError("مرسوله تحویل داده شده و قابل ویرایش نیست.")

    def validate_package_operation(self, shipment: OrderShipment):
        if shipment.status in ['dispatched', 'delivered']:
            raise ValidationError("مرسوله ارسال شده است و تغییر در بسته‌بندی مجاز نیست.")
    
    def generate_code(self, order_code) -> str:
        """ تولید شناسه یکتا برای لیبل """
        return f"{order_code}"

    # ========== CHANGE STATUS ========== #
    @transaction.atomic
    def change_shipment_status(self, shipment: OrderShipment, new_status_code: str, user: User) -> OrderShipment:
        """
        تغییر وضعیت مرسوله (مثلاً ارسال شده، تحویل شده) و ثبت لاگ.
        """
        # ===== بررسی وضعیت ===== #
        if shipment.status == 'delivered':
            raise ValidationError("مرسوله تحویل شده و وضعیت آن نهایی است.")

        old_status = shipment.status
        if old_status == new_status_code:
            return shipment

        # ===== محاسبه فیلد ها ===== #
        update_fields = self._get_status_update_fields(shipment, new_status_code)
        
        if not update_fields:
            return shipment

        # ===== ثبت لاگ ===== #
        self.audit_service.record_log(
            user=user,
            obj=shipment,
            action='SHIPMENT_UPDATE',
            changes={
                'field': 'status',
                'from': old_status,
                'to': new_status_code,
                'tracking_code': shipment.tracking_code
            },
            description=_(f"تغییر وضعیت مرسوله به {new_status_code}")
        )

        # ===== به روز کردن فیلدهای مربوط ===== #
        for field, value in update_fields.items():
            setattr(shipment, field, value)
        
        # ===== ذخیره ===== #
        shipment.save(update_fields=update_fields.keys())
        return shipment
    
    
    def approve_shipment(self, shipment: OrderShipment, user: User) -> OrderShipment:
        """
        تایید تحویل به مشتری و آپدیت وضعیت سفارش مادر
        """
        # ===== اعتبارسنجی وضعیت فعلی ===== #
        if shipment.status == 'delivered':
            raise ValidationError("مرسوله قبلاً تحویل شده و وضعیت آن نهایی است.")
        
        old_status = shipment.status
        approve_status = "delivered"
        
        # ===== آپدیت فیلدهای مرسوله ===== #
        update_fields = self._get_status_update_fields(shipment, approve_status)
        if not update_fields:
            return shipment
        
        # ===== ثبت لاگ تغییر وضعیت ===== #
        for field, value in update_fields.items():
            setattr(shipment, field, value)

        # ===== ثبت لاگ مرسوله ===== #
        self.audit_service.record_log(
            user=user,
            obj=shipment,
            action='SHIPMENT_APPROVE',
            changes={
                'field': 'status',
                'from': old_status,
                'to': approve_status,
                'tracking_code': shipment.tracking_code
            },
            description=_(f"تایید نهایی مرسوله توسط مدیریت")
        )
        
        # ===== ذخیره تغییرات مرسوله ===== #
        shipment.save(update_fields=list(update_fields.keys()))

        # ===== تغییر وضعیت سفارش ===== #
        order = shipment.order        
        order_status = OrderStatus.objects.get_status_by_code("DELIVERED")
        if order.current_status.internal_code not in ["delivered", 'deliver']:
            order.current_status = order_status
            order.save()

        return shipment

    # ========== HELPER FUNCTIONS ========== #
    def _get_status_update_fields(self, shipment: OrderShipment, new_status_code: str) -> Dict[str, Any]:
        """Internal Helper Logic"""
        update_fields = {'status': new_status_code}
        current_time = timezone.now()

        if new_status_code == 'dispatched' and not shipment.dispatched_at:
            update_fields['dispatched_at'] = current_time
            
        elif new_status_code == 'delivered' and not shipment.delivered_at:
            update_fields['delivered_at'] = current_time
            if not shipment.dispatched_at:
                update_fields['dispatched_at'] = current_time

        return update_fields
    
    # ===== APPROVE ORDER ENTRY (WAREHOUSE RECEIPT) ===== #
    @transaction.atomic
    def approve_order_entry_to_warehouse(self, order: Order, user: User) -> Order:
        """
        تایید ورود کالا به انبار (Receipt Confirmation).
        زمانی که تولید تمام شده و کالا فیزیکی به انبار می‌رسد، انباردار تایید می‌کند.
        وضعیت سفارش به 'آماده ارسال' (Approve Type) تغییر می‌کند.
        """

        current_status = order.current_status

        # ===== دریافت وضعیت تایید انبار ===== #
        warehouse_approved_status = OrderStatus.objects.filter(
            group__code=current_status.group.code, 
            status_type='approve'
        ).first()
        
        if not warehouse_approved_status:
            raise ValidationError("وضعیت 'تایید انبار' (Approve) تعریف نشده است.")

        # ===== بررسی وضعیت فعلی سفارش ===== #
        if order.current_status == warehouse_approved_status:
             raise ValidationError("این سفارش قبلاً توسط انبار تایید (رسید) شده است.")

        old_status_name = order.current_status.name if order.current_status else "نامشخص"

        # ===== تغییر وضعیت سفارش به 'تایید انبار' ===== #
        order.current_status = warehouse_approved_status
        order.save(update_fields=['current_status', 'updated_at'])

        # ===== بررسی و به‌روزرسانی وضعیت مرسوله‌ها ===== #
        pending_shipments = order.shipments.exclude(status__in=['dispatched', 'delivered', 'returned'])
        
        # ===== وضعیت ===== #
        pending_shipments.update(status='ready_to_ship')

        # ===== ثبت لاگ ===== #
        self.audit_service.record_log(
            user=user,
            obj=order,
            action='WAREHOUSE_CONFIRM',
            changes={
                'from_status': old_status_name,
                'to_status': warehouse_approved_status.name,
            },
            description=_("تایید ورود کالا به انبار (اتمام تولید)")
        )
        
        return order
