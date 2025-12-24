from typing import Dict, Any, List

from rest_framework.exceptions import ValidationError, NotFound
from django.utils.translation import gettext_lazy as _
from django.db import transaction

from apps.permissions import AppPermissionChecker
from core.models import User, Order, OrderShipment, OrderPackage, OrderCostSheet, OrderCostReport
from core.order.services import LogisticsService
from core.logger.services import LoggerService

# ========== Warehouse App Service ========== #
class WarehouseAppService:
    """
    سرویس اپلیکیشن برای مدیریت عملیات انبارداری و ارسال (Warehouse Operations).
    """
    def __init__(self):
        self._logistic_domain = LogisticsService()
        self.audit_service = LoggerService()
    
    # ========== GET SHIPMENT DETAILS ========== #
    def get_shipment_details(self, user: User, shipment_id: int) -> OrderShipment:
        AppPermissionChecker.check_has_permission(user, 'view_ordershipment')
        
        shipment = OrderShipment.objects.get_shipment_with_details(shipment_id)
        if not shipment:
            raise NotFound("مرسوله یافت نشد.")
        return shipment
    
    # ========== CREATE SHIPMENT AND PACKAGES ========== #
    @transaction.atomic
    def create_shipment_and_packages(self, user: User, order_id: int, data: Dict[str, Any]) -> OrderShipment:
        """ ایجاد مرسوله و بسته‌های اولیه به صورت یکجا """
        AppPermissionChecker.check_has_permission(user, 'add_ordershipment')

        # ===== دریافت سفارش ===== #
        try:
            order = Order.objects.get(pk=order_id)
        except Order.DoesNotExist:
            raise NotFound("سفارش یافت نشد.")
        
        # ===== اعتبارسنجی روش ارسال ===== #
        method_type = data.get('delivery_method')
        valid_methods = dict(OrderShipment.METHOD_CHOICES).keys()
        if method_type not in valid_methods:
             raise ValidationError(f"روش ارسال '{method_type}' نامعتبر است.")
        
        # ===== ایجاد مرسوله با منیجر ===== #
        shipment = OrderShipment.objects.create(
            order=order,
            delivery_method=method_type,
            destination_address=data.get('destination_address', order.address),
            tracking_code=self._logistic_domain.generate_code(order.order_code),
            driver_info=data.get('driver_info'),
            shipping_cost_real=data.get('shipping_cost_real') or 0,
            expected_delivery_date=data.get('expected_delivery_date'),
            status="pending"
        )
        
        # ===== ایجاد بسته‌ها (Packages) ===== #
        packages_data: List[Dict] = data.get('packages', [])
        for pkg_data in packages_data:
            customer_name = pkg_data.get('customer_name') or (order.user.get_full_name() if order.user else "Unknown")
            phone_number = pkg_data.get('phone_number') or (order.address.phone_number if order.address else "")
            address_text = pkg_data.get('address') or (str(order.address) if order.address else "")
            
            OrderPackage.objects.create(
                shipment=shipment,
                label_uuid=self._logistic_domain.generate_code(order.order_code),
                customer_name=customer_name,
                phone_number=phone_number,
                address=address_text,
                content_summary=pkg_data.get('content_summary'),
                packed_by=user,
            )
        
        # ===== ثبت لاگ ===== #
        self.audit_service.record_log(
            user=user,
            obj=shipment,
            action='CREATE_SHIPMENT',
            changes={
                'order_code': order.order_code,
                'packages_count': len(packages_data),
                'method': method_type
            },
            description=_(f"ایجاد مرسوله جدید برای سفارش {order.order_code}")
        )
        
        return shipment
        
    # ========== UPDATE SHIPMENT ========== #
    @transaction.atomic
    def update_shipment(self, user: User, shipment_id: int, data: Dict[str, Any]) -> OrderShipment:
        """ ویرایش اطلاعات مرسوله """
        AppPermissionChecker.check_has_permission(user, 'change_ordershipment')
        # ===== دریافت مرسوله ===== #
        shipment = OrderShipment.objects.get_by_id(shipment_id)
        if not shipment:
            raise NotFound("مرسوله یافت نشد.")
        # ===== بررسی عدم تغییر فیلدهای سیستمی ===== #
        if 'status' in data:
             raise ValidationError("برای تغییر وضعیت از متد change_status استفاده کنید.")
         # ===== بررسی قوانین دامنه ===== #
        self._logistic_domain.validate_shipment_modification(shipment)
        
        # ===== اعمال ویرایش ===== #
        for key, value in data.items():
            if hasattr(shipment, key):
                setattr(shipment, key, value)
        shipment.save()

        # ===== ثبت لاگ ===== #
        self.audit_service.record_log(
            user=user,
            obj=shipment,
            action='UPDATE_SHIPMENT',
            changes={'updated_fields': list(data.keys())},
            description=_(f"ویرایش اطلاعات مرسوله")
        )
        return shipment
    
    # ========== DELETE SHIPMENT ========== #
    @transaction.atomic
    def delete_shipment(self, user: User, shipment_id: int) -> OrderShipment:
        """ حذف مرسوله """
        AppPermissionChecker.check_has_permission(user, 'delete_ordershipment')
        # ===== بررسی وجود ===== #
        shipment = OrderShipment.objects.get_by_id(shipment_id)
        if not shipment:
            raise NotFound("مرسوله یافت نشد.")
        # ===== بررسی قوانین ===== #
        tracking_code = shipment.tracking_code
        order_code = shipment.order.order_code
        # ===== بررسی قوانین دامنه ===== #
        self._logistic_domain.validate_shipment_modification(shipment)
        shipment.delete()
        # ===== ثبت لاگ ===== #
        self.audit_service.record_log(
            user=user,
            obj=None,
            action='DELETE_SHIPMENT',
            changes={'deleted_shipment_id': shipment_id, 'tracking_code': tracking_code, 'order_code': order_code},
            description=_(f"حذف مرسوله سفارش")
        )
    
    # ========== CHANGE SHIPMENT STATUS ========== #
    @transaction.atomic
    def change_shipment_status(self, user: User, shipment_id: int, new_status_code: str) -> OrderShipment:
        """ تغییر وضعیت مرسوله """
        AppPermissionChecker.check_has_permission(user, 'change_ordershipment')
        # ===== بررسی وجود ===== #
        shipment = OrderShipment.objects.get_by_id(shipment_id)
        if not shipment:
            raise NotFound("مرسوله یافت نشد.")
        # ===== بررسی توسط سرویس دامنه و بروزرسانی وضعیت ===== #
        return self._logistic_domain.change_shipment_status(shipment, new_status_code, user)

    # ========== ADD PACKAGE TO SHIPMENT ========== #
    @transaction.atomic
    def add_package_to_shipment(self, user: User, shipment_id: int, data: Dict[str, Any]) -> OrderPackage:
        """ اضافه کردن بسته تکی """
        AppPermissionChecker.check_has_permission(user, 'add_ordershipment')
        
        shipment = OrderShipment.objects.get_by_id(shipment_id)
        if not shipment:
            raise NotFound("مرسوله یافت نشد.")
        # ===== بررسی قوانین دامنه ===== #
        self._logistic_domain.validate_package_operation(shipment)
        # ===== اضافه کردن بسته ===== #
        order = shipment.order
        customer_name = data.get('customer_name') or (order.user.get_full_name() if order.user else "")
        phone_number = data.get('phone_number') or (order.address.phone_number if order.address else "")
        address_text = data.get('address') or (str(order.address) if order.address else "")
        # ===== ایجاد بسته بندی ===== #
        package = OrderPackage.objects.create(
            shipment=shipment,
            label_uuid=self._logistic_domain.generate_code(order.order_code),
            customer_name=customer_name,
            phone_number=phone_number,
            address=address_text,
            content_summary=data.get('content_summary'),
            packed_by=user
        )
        
        # ===== ثبت لاگ ===== #
        self.audit_service.record_log(
            user=user,
            obj=shipment,
            action='ADD_PACKAGE',
            changes={'package_id': package.id, 'label': package.label_uuid},
            description=_(f"افزودن بسته جدید به مرسوله")
        )
        
        return package
    
    # ========== DELETE PACKAGE FROM SHIPMENT ========== #
    @transaction.atomic
    def delete_package_from_shipment(self, user: User, package_id: int):
        """ حذف بسته """
        AppPermissionChecker.check_has_permission(user, 'delete_package')
        # ===== بررسی وجود بسته ===== #
        try:
            package = OrderPackage.objects.get(id=package_id)
        except OrderPackage.DoesNotExist:
            raise NotFound("بسته یافت نشد.")
        # ===== بررسی قوانین دامنه ===== #
        shipment = package.shipment
        label = package.label_uuid
        # ===== بررسی قوانین دامنه ===== #
        self._logistic_domain.validate_package_operation(shipment)
        package.delete()
        # ===== ثبت لاگ ===== #
        self.audit_service.record_log(
            user=user,
            obj=shipment,
            action='DELETE_PACKAGE',
            changes={'deleted_package_id': package_id, 'label': label},
            description=_(f"حذف بسته از مرسوله")
        )
    
    # ========== ADD LOGISTIC COST REPORT ========== #
    def add_logistic_cost_report(self, user: User, order_id: int, data: Dict[str, Any]) -> OrderCostSheet:
        AppPermissionChecker.check_has_permission(user, 'add_ordercostreport')
        # ===== دریافت سند مالی ===== #
        try:
            sheet = OrderCostSheet.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            raise NotFound("سفارش یافت نشد.")
        # ===== ثبت لاگ ===== #
        self.audit_service.record_log(
            user=user,
            obj=sheet,
            action='LOGISTIC_COST_REPORT',
            changes={'title': data.get('title'), 'amount_items': len(data.get('items', []))},
            description=_(f"ثبت گزارش هزینه لجستیک توسط انبار")
        )
        
        return self._cost_domain.create_cost_report(
            sheet=sheet,
            title=data['title'],
            department='logistics',
            description=data.get('description', ''),
            attachment=data.get('attachment'),
            items_data=data['items'],
            user=user
        )    
