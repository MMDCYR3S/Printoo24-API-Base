from typing import Dict, Any, List

from rest_framework.exceptions import ValidationError, NotFound
from django.db import transaction

from apps.permissions import AppPermissionChecker
from core.models import User, Order, OrderShipment, OrderPackage, OrderCostSheet
from core.domain.commerce.order import (
    LogisticDomainService,
    OrderCostDomainService,
    OrderRepository,
    ShipmentRepository,
    PackageRepository
)

# ========== Warehouse App Service ========== #
class WarehouseAppService:
    """
    سرویس اپلیکیشن برای مدیریت عملیات انبارداری و ارسال (Warehouse Operations).
    """
    def __init__(self):
        # ===== ریپازیتوری ها ===== #
        self._order_repo = OrderRepository()
        self._shipment_repo = ShipmentRepository()
        self._package_repo = PackageRepository()
        # ===== سرویس های دامنه مورد نیاز ===== #
        self._logistic_domain = LogisticDomainService()
        self._cost_domain = OrderCostDomainService() 

    def _get_order_and_validate_access(self, user: User, order_id: int) -> Order:
        """ متد کمکی برای دریافت سفارش """
        order = self._order_repo.get_by_id(order_id)
        if not order:
            raise ValidationError("سفارش یافت نشد.")
        return order

    # ==================================================
    # ========== 1. عملیات مرسوله (Shipment Operations) ==========
    # ==================================================

    def _get_order(self, order_id: int) -> Order:
        order = self._order_repo.get_by_id(order_id)
        if not order:
            raise NotFound("سفارش یافت نشد.")
        return order

    def _get_shipment(self, shipment_id: int) -> OrderShipment:
        shipment = self._shipment_repo.get_by_id(shipment_id)
        if not shipment:
            raise NotFound("مرسوله یافت نشد.")
        return shipment
    
    # ========== GET SHIPMENT DETAILS ========== #
    def get_shipment_details(self, user: User, shipment_id: int) -> OrderShipment:
        AppPermissionChecker.check_has_permission(user, 'view_ordershipment')
        
        # استفاده از متد خاص ریپازیتوری برای جوین‌ها
        shipment = self._shipment_repo.get_shipment_with_details(shipment_id)
        if not shipment:
            raise NotFound("مرسوله یافت نشد.")
        return shipment
    
    # ========== CREATE SHIPMENT AND PACKAGES ========== #
    @transaction.atomic
    def create_shipment_and_packages(self, user: User, order_id: int, data: Dict[str, Any]) -> OrderShipment:
        """ ایجاد مرسوله و بسته‌های اولیه به صورت یکجا """
        AppPermissionChecker.check_has_permission(user, 'add_ordershipment')

        # ===== دریافت روش ارسال ===== #
        method_type = data.get('delivery_method')
        
        # ===== اعتبارسنجی روش ارسال ===== #
        valid_methods = dict(OrderShipment.METHOD_CHOICES).keys()
        if method_type not in valid_methods:
             raise ValidationError(f"روش ارسال '{method_type}' نامعتبر است.")
        
        order = self._get_order(order_id)
        # ===== ایجاد مرسوله ===== #
        shipment = self._shipment_repo.create({
            "order": order,
            "delivery_method": method_type,
            "destination_address": data.get('destination_address', order.address),
            "tracking_code": self._logistic_domain.generate_code(order.order_code),
            "driver_info": data.get('driver_info'),
            "shipping_cost_real": data.get('shipping_cost_real', ""),
            "expected_delivery_date": data.get('expected_delivery_date'),
            "status": "pending"
        })
        
        # ===== ایجاد اطلاعات لیبل ===== #
        packages_data: List[Dict] = data.get('packages', [])
        for index, pkg_data in enumerate(packages_data):
            customer_name = pkg_data.get('customer_name') or (order.user.get_full_name() if order.user else "Unknown")
            phone_number = pkg_data.get('phone_number') or (order.address.phone_number if order.address else "")
            address_text = pkg_data.get('address') or (order.address.full_text if order.address else "")
            # ===== ایجاد لیبل بسته بندی ===== #
            self._package_repo.create({
                "shipment": shipment,
                "label_uuid": self._logistic_domain.generate_code(order.order_code),
                "customer_name": customer_name,
                "phone_number": phone_number,
                "address": address_text,
                "content_summary": pkg_data.get('content_summary'),
                "packed_by": user,
            })
        
        return shipment
    
    # ========== UPDATE SHIPMENT ========== #
    @transaction.atomic
    def update_shipment(self, user: User, shipment_id: int, data: Dict[str, Any]) -> OrderShipment:
        """ ویرایش اطلاعات مرسوله """
        AppPermissionChecker.check_has_permission(user, 'change_ordershipment')
        # ===== دریافت مرسوله ===== #
        shipment = self._get_shipment(shipment_id)
        if 'delivery_method_id' in data:
             raise ValidationError("لطفا از فیلدهای معتبر استفاده کنید.")
        # ===== بررسی قوانین دامنه ===== #
        self._logistic_domain.validate_shipment_modification(shipment)
        # ===== اعمال ویرایش ===== #
        if data:
            shipment = self._shipment_repo.update(shipment, data)
        return shipment
    
    # ========== DELETE SHIPMENT ========== #
    @transaction.atomic
    def delete_shipment(self, user: User, shipment_id: int) -> OrderShipment:
        """ حذف مرسوله """
        AppPermissionChecker.check_has_permission(user, 'delete_ordershipment')
        # ===== بررسی وجود ===== #
        shipment = self._get_shipment(shipment_id)
        # ===== بررسی قوانین ===== #
        self._logistic_domain.validate_shipment_modification(shipment)
        self._shipment_repo.delete(shipment)
    
    # ========== CHANGE SHIPMENT STATUS ========== #
    @transaction.atomic
    def change_shipment_status(self, user: User, shipment_id: int, new_status_code: str) -> OrderShipment:
        """ تغییر وضعیت مرسوله """
        AppPermissionChecker.check_has_permission(user, 'change_ordershipment')
        # ===== بررسی وجود ===== #
        shipment = self._get_shipment(shipment_id)
        # ===== بررسی وضعیت ===== #
        update_fields = self._logistic_domain.apply_status_change_logic(shipment, new_status_code)
        # ===== اعمال تغییر وضعیت ===== #
        if update_fields:
            shipment = self._shipment_repo.update(shipment, update_fields)
            
        return shipment
        
    # ========== ADD PACKAGE TO SHIPMENT ========== #
    @transaction.atomic
    def add_package_to_shipment(self, user: User, shipment_id: int, data: Dict[str, Any]) -> OrderPackage:
        """ اضافه کردن بسته تکی """
        AppPermissionChecker.check_has_permission(user, 'add_ordershipment')
        
        shipment = self._get_shipment(shipment_id)
        # ===== بررسی قوانین دامنه ===== #
        self._logistic_domain.validate_package_operation(shipment)
        # ===== اضافه کردن بسته ===== #
        order = shipment.order
        customer_name = data.get('customer_name') or (order.user.get_full_name() if order.user else "")
        phone_number = data.get('phone_number') or (order.address.phone_number if order.address else "")
        address_text = data.get('address') or (order.address.full_text if order.address else "")
                # ===== ایجاد بسته بندی ===== #
        package = self._package_repo.create({
            "shipment": shipment,
            "label_uuid": self._logistic_domain.generate_label_code(shipment),
            "customer_name": customer_name,
            "phone_number": phone_number,
            "address": address_text,
            "content_summary": data.get('content_summary'),
            "packed_by": user
        })
        return package
    
    # ========== DELETE PACKAGE FROM SHIPMENT ========== #
    @transaction.atomic
    def delete_package_from_shipment(self, user: User, package_id: int):
        """ حذف بسته """
        AppPermissionChecker.check_has_permission(user, 'delete_package')
        
        package = self._package_repo.get_by_id(package_id)
        if not package:
            raise NotFound("بسته یافت نشد.")
        # ===== بررسی قوانین دامنه ===== #
        self._logistic_domain.validate_package_operation(package.shipment)
        # ===== حذف ===== #
        self._package_repo.delete(package)
    
    # ========== ADD LOGISTIC COST REPORT ========== #
    def add_logistic_cost_report(self, user: User, order_id: int, data: Dict[str, Any]) -> OrderCostSheet:
        AppPermissionChecker.check_has_permission(user, 'add_ordercostreport')
        order = self._get_order(order_id)
        
        return self._cost_domain.create_cost_report(
            order=order,
            title=data['title'],
            description=data.get('description', ''),
            attachment=data.get('attachment'),
            items_data=data['items'],
            user=user
        )    
    