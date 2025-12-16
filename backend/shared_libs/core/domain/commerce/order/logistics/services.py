from typing import List, Dict, Any, Optional
from django.db import transaction
from django.db.models import Max
from django.utils import timezone
from django.core.exceptions import ValidationError

from core.models import Order, User, OrderShipment, OrderPackage

# ========== Logisitic Domain Service ========== #
class LogisticDomainService:
    """
    سرویس دامنه برای مدیریت منطق لجستیک، مرسوله‌ها و بسته‌بندی.
    وظایف: ایجاد مرسوله، اضافه کردن بسته‌ها، به‌روزرسانی هزینه واقعی ارسال.
    """

    def validate_shipment_modification(self, shipment: OrderShipment):
        if shipment.status == 'delivered':
            raise ValidationError("مرسوله تحویل داده شده و قابل ویرایش نیست.")

    def validate_package_operation(self, shipment: OrderShipment):
        if shipment.status in ['dispatched', 'delivered']:
            raise ValidationError("مرسوله ارسال شده است و تغییر در بسته‌بندی مجاز نیست.")
    
    def generate_code(self, order_code) -> str:
        """ تولید شناسه یکتا برای لیبل """
        return f"{order_code}"

    def apply_status_change_logic(self, shipment: OrderShipment, new_status_code: str) -> Dict[str, Any]:
        if shipment.status == new_status_code:
            return {}

        update_fields = {'status': new_status_code}
        current_time = timezone.now()

        if new_status_code == 'dispatched' and not shipment.dispatched_at:
            update_fields['dispatched_at'] = current_time
            
        elif new_status_code == 'delivered' and not shipment.delivered_at:
            update_fields['delivered_at'] = current_time
            if not shipment.dispatched_at:
                update_fields['dispatched_at'] = current_time

        return update_fields
