from typing import List, Dict, Any, Optional
from django.db import transaction
from django.db.models import Max
from django.utils import timezone
from django.core.exceptions import ValidationError

from core.models import Order, User, OrderShipment, OrderPackage
from .repositories import ShipmentRepository, PackageRepository, DeliveryMethodRepository

# ========== Logisitic Domain Service ========== #
class LogisticDomainService:
    """
    سرویس دامنه برای مدیریت منطق لجستیک، مرسوله‌ها و بسته‌بندی.
    وظایف: ایجاد مرسوله، اضافه کردن بسته‌ها، به‌روزرسانی هزینه واقعی ارسال.
    """
    def __init__(self):
        self._shipment_repo = ShipmentRepository()
        self._package_repo = PackageRepository()
        self._delivery_method_repo = DeliveryMethodRepository()

    @transaction.atomic
    def create_shipment_and_packages(self, order: Order, data: Dict[str, Any], creator: User) -> OrderShipment:
        """
        ایجاد یک مرسوله جدید و آیتم‌های بسته‌بندی آن.
        """
        # ===== اعتبارسنجی متد ===== #
        delivery_method = self._delivery_method_repo.get_by_id(data['delivery_method_id'])
        if not delivery_method:
            raise ValidationError("روش ارسال نامعتبر است.")

        # ===== ایجاد مرسوله ===== #
        shipment = self._shipment_repo.create({
            "order": order,
            "delivery_method": delivery_method,
            "destination_address": data.get('destination_address', order.address), # استفاده از آدرس سفارش
            "tracking_code": data.get('tracking_code'),
            "shipping_cost_real": data.get('shipping_cost_real', delivery_method.base_price),
            "expected_delivery_date": data.get('expected_delivery_date'),
        })

        # ===== ایجاد بسته ===== #
        packages_data: List[Dict] = data.get('packages', [])
        for index, package_data in enumerate(packages_data):
            self._package_repo.create({
                "shipment": shipment,
                "box_number": index + 1,
                "weight_grams": package_data.get('weight_grams', 0),
                "width_cm": package_data.get('width_cm', 0),
                "length_cm": package_data.get('length_cm', 0),
                "height_cm": package_data.get('height_cm', 0),
                "content_summary": package_data.get('content_summary'),
                "packed_by": creator,
            })

        return shipment

    @transaction.atomic
    def update_shipment_details(self, shipment_id: int, data: Dict[str, Any]) -> OrderShipment:
        """ 
        ویرایش اطلاعات مرسوله (کد رهگیری، راننده، هزینه و...) 
        """
        shipment = self._shipment_repo.get_by_id(shipment_id)
        if not shipment:
            raise ValidationError("مرسوله یافت نشد.")

        if shipment.status == 'delivered':
             raise ValidationError("مرسوله تحویل داده شده و قابل ویرایش نیست.")

        fields_to_update = {}
        
        if 'tracking_code' in data:
            fields_to_update['tracking_code'] = data['tracking_code']
        if 'driver_info' in data:
            fields_to_update['driver_info'] = data['driver_info']
        if 'shipping_cost_real' in data:
            fields_to_update['shipping_cost_real'] = data['shipping_cost_real']
        if 'destination_address_id' in data:
            fields_to_update['destination_address_id'] = data['destination_address_id']
            
        if fields_to_update:
            shipment = self._shipment_repo.update(shipment, fields_to_update)
            
        return shipment

    @transaction.atomic
    def change_shipment_status(self, shipment_id: int, new_status_code: str, user: User) -> OrderShipment:
        """ 
        تغییر وضعیت مرسوله و ثبت زمان‌های ارسال/تحویل
        """
        shipment = self._shipment_repo.get_by_id(shipment_id)
        if not shipment:
            raise ValidationError("مرسوله یافت نشد.")

        if shipment.status == new_status_code:
            return shipment

        update_fields = {'status': new_status_code}
        current_time = timezone.now()

        if new_status_code == 'dispatched' and not shipment.dispatched_at:
            update_fields['dispatched_at'] = current_time
            
        elif new_status_code == 'delivered' and not shipment.delivered_at:
            update_fields['delivered_at'] = current_time
            if not shipment.dispatched_at:
                update_fields['dispatched_at'] = current_time

        shipment = self._shipment_repo.update(shipment, update_fields)
        return shipment

    # ==========================================
    # ========== Package Logic ================
    # ==========================================

    @transaction.atomic
    def create_package(self, shipment_id: int, data: Dict[str, Any], user: User) -> OrderPackage:
        """ اضافه کردن یک بسته جدید به مرسوله موجود """
        shipment = self._shipment_repo.get_by_id(shipment_id)
        if not shipment:
            raise ValidationError("مرسوله یافت نشد.")
            
        if shipment.status in ['dispatched', 'delivered']:
            raise ValidationError("مرسوله ارسال شده است و نمی‌توان بسته جدید اضافه کرد.")

        # محاسبه شماره جعبه بعدی (Auto Increment Box Number)
        max_box = shipment.packages.aggregate(Max('box_number'))['box_number__max'] or 0
        next_box_number = max_box + 1

        package = self._package_repo.create({
            "shipment": shipment,
            "box_number": next_box_number,
            "weight_grams": data.get('weight_grams', 0),
            "width_cm": data.get('width_cm', 0),
            "length_cm": data.get('length_cm', 0),
            "height_cm": data.get('height_cm', 0),
            "content_summary": data.get('content_summary'),
            "packed_by": user
        })
        return package

    @transaction.atomic
    def delete_package(self, package_id: int):
        """ حذف بسته """
        package = self._package_repo.get_by_id(package_id)
        if not package:
            raise ValidationError("بسته یافت نشد.")
            
        if package.shipment.status in ['dispatched', 'delivered']:
            raise ValidationError("مرسوله ارسال شده است و نمی‌توان بسته‌های آن را حذف کرد.")
            
        package.delete()
    
    def get_shipment_with_details(self, shipment_id: int) -> Optional[OrderShipment]:
        """ 
        دریافت مرسوله با تمام جزئیات (متد ارسال، آدرس، بسته‌ها)
        """
        return self._shipment_repo.get_shipment_with_details(shipment_id)
    