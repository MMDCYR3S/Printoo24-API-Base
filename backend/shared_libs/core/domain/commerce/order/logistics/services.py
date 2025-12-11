import uuid
from typing import List, Dict, Any
from django.db import transaction
from django.core.exceptions import ValidationError

from core.models import Order, User, OrderShipment
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
        # 1. اعتبارسنجی متد ارسال
        delivery_method = self._delivery_method_repo.get_by_id(data['delivery_method_id'])
        if not delivery_method:
            raise ValidationError("روش ارسال نامعتبر است.")

        # 2. ایجاد مرسوله (Shipment)
        shipment = self._shipment_repo.create({
            "order": order,
            "delivery_method": delivery_method,
            "destination_address": data.get('destination_address', order.address), # استفاده از آدرس سفارش
            "tracking_code": data.get('tracking_code'),
            "shipping_cost_real": data.get('shipping_cost_real', delivery_method.base_price),
            "expected_delivery_date": data.get('expected_delivery_date'),
        })

        # 3. ایجاد بسته‌ها (Packages)
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
