from typing import Dict, Any

from rest_framework.exceptions import ValidationError, PermissionDenied

from apps.permissions import AppPermissionChecker
from core.models import User, Order, OrderShipment, OrderPackage, OrderCostSheet
from core.domain.commerce.order import (
    LogisticDomainService,
    OrderCostDomainService,
    OrderRepository
)

# ========== Warehouse App Service ========== #
class WarehouseAppService:
    """
    سرویس اپلیکیشن برای مدیریت عملیات انبارداری و ارسال (Warehouse Operations).
    """
    def __init__(self):
        # ===== تزریق وابستگی‌های دامنه ===== #
        self._logistic_domain = LogisticDomainService()
        self._cost_domain = OrderCostDomainService() 
        self._order_repo = OrderRepository()

    def _get_order_and_validate_access(self, user: User, order_id: int) -> Order:
        """ متد کمکی برای دریافت سفارش """
        order = self._order_repo.get_by_id(order_id)
        if not order:
            raise ValidationError("سفارش یافت نشد.")
        return order

    # ==================================================
    # ========== 1. عملیات مرسوله (Shipment Operations) ==========
    # ==================================================

    def get_shipment_details(self, user: User, shipment_id: int) -> OrderShipment:
        """ 
        مشاهده جزئیات کامل مرسوله 
        """
        # ===== چک دسترسی: مشاهده مرسوله ===== #
        AppPermissionChecker.check_has_permission(user, 'view_ordershipment')
        
        shipment = self._logistic_domain.get_shipment_with_details(shipment_id)
        if not shipment:
            raise ValidationError("مرسوله یافت نشد.")
            
        return shipment

    def create_shipment_and_packages(self, user: User, order_id: int, data: Dict[str, Any]) -> OrderShipment:
        """ 
        عملیات: ایجاد مرسوله و بسته‌ها.
        """
        # ===== چک دسترسی: ایجاد مرسوله ===== #
        AppPermissionChecker.check_has_permission(user, 'add_ordershipment')

        order = self._get_order_and_validate_access(user, order_id)
        
        shipment = self._logistic_domain.create_shipment_and_packages(order, data, user)
            
        return shipment

    def update_shipment(self, user: User, shipment_id: int, data: Dict[str, Any]) -> OrderShipment:
        """ 
        به‌روزرسانی جزئیات مرسوله (کد رهگیری، آدرس مقصد، هزینه واقعی).
        """
        # ===== چک دسترسی: به‌روزرسانی مرسوله ===== #
        AppPermissionChecker.check_has_permission(user, 'change_ordershipment')
        
        # [توجه]: سرویس دامنه Shipment باید دسترسی به آبجکت Shipment را چک کند.
        shipment = self._logistic_domain.update_shipment_details(shipment_id, data)
        
        # # به‌روزرسانی هزینه در دامنه مالی
        # if 'shipping_cost_real' in data:
        #     self._cost_domain.update_shipping_cost_report(
        #         order=shipment.order,
        #         new_amount=data['shipping_cost_real'],
        #         user=user
        #     )
            
        return shipment
        
    def change_shipment_status(self, user: User, shipment_id: int, new_status_code: str) -> OrderShipment:
        """ تغییر وضعیت مرسوله (Dispatched, Delivered) """
        # ===== چک دسترسی: تغییر وضعیت ارسال ===== #
        AppPermissionChecker.check_has_permission(user, 'change_ordershipment')
        
        return self._logistic_domain.change_shipment_status(shipment_id, new_status_code, user)
        
    # ==================================================
    # ========== 2. عملیات بسته‌بندی (Package Operations) ==========
    # ==================================================
    
    def add_package_to_shipment(self, user: User, shipment_id: int, data: Dict[str, Any]) -> OrderPackage:
        """ اضافه کردن یک بسته جدید به مرسوله موجود """
        # ===== چک دسترسی: ایجاد بسته ===== #
        AppPermissionChecker.check_has_permission(user, 'add_ordershipment')
        
        return self._logistic_domain.create_package(shipment_id, data, user)
        
    def delete_package_from_shipment(self, user: User, package_id: int):
        """ حذف یک بسته از مرسوله """
        # ===== چک دسترسی: حذف بسته ===== #
        AppPermissionChecker.check_has_permission(user, 'delete_package')
        
        return self._logistic_domain.delete_package(package_id)

    # ==================================================
    # ========== 3. عملیات هزینه لجستیک (Ad-hoc Cost) ==========
    # ==================================================
    
    def add_logistic_cost_report(self, user: User, order_id: int, data: Dict[str, Any]) -> OrderCostSheet:
        """
        عملیات: اضافه کردن گزارش هزینه لجستیک جدید (مانند هزینه بیمه، بسته‌بندی اضافی).
        """
        # ===== چک دسترسی: ثبت هزینه لجستیک ===== #
        AppPermissionChecker.check_has_permission(user, 'add_ordercostreport')

        order = self._get_order_and_validate_access(user, order_id)
        
        # فراخوانی سرویس دامنه مالی برای ثبت گزارش هزینه
        cost_report = self._cost_domain.create_cost_report(
            order=order,
            title=data['title'],
            description=data.get('description', ''),
            attachment=data.get('attachment'),
            items_data=data['items'],
            user=user
        )
        return cost_report

