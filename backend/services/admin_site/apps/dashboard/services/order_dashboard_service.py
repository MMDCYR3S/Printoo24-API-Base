import logging
from typing import List, Dict, Any
from decimal import Decimal

from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core.exceptions import ValidationError

from core.models import User, Order, OrderItem, OrderStatus, Product, Address
from core.order.services import OrderService
from core.financial.services import FinancialService

# ========== LOGGER ========== #
logger = logging.getLogger('dashboard.services.order_dashboard')

# ========== ORDER DASHBOARD SERVICE ========== #
class OrderDashboardService:
    """
    سرویس اپلیکیشن برای مدیریت سفارشات در پنل ادمین (داشبورد).
    شامل: ثبت سفارش اختصاصی، ویرایش سفارش، لیست و حذف گروهی.
    """
    def __init__(self):
        self.order_domain = OrderService()
        # self.financial_service = FinancialService()
        
    # ========== READ OPERATIONS ========== #
    def get_all_orders_queryset(self):
        """ لیست سفارشات برای جدول (بهینه شده) """
        return Order.objects.select_related('user', 'current_status')\
            .prefetch_related('order_item_order')\
            .order_by('-created_at')

    def get_order_detail(self, order_id: int):
        """ جزئیات کامل سفارش """
        return self.order_domain.get_order_by_id(order_id)
        
    # ============ CREATE CUSTOM ORDER ============ #
    @transaction.atomic
    def create_custom_order(self, admin_user: User, data: Dict[str, Any]) -> Order:
        """
        ثبت سفارش اختصاصی توسط ادمین.
        ادمین می‌تواند قیمت‌ها را دستی وارد کند یا بگذارد سیستم محاسبه کند.
        """
        logger.info(f"Dashboard: Creating custom order by Admin {admin_user.id}")
        # ===== استخراج داده اصلی ===== #
        user_id = data.get('user_id')
        address_id = data.get('address_id')
        items_data = data.get('items', [])
        total_price_override = data.get('price')
        # ===== اگر کاربر آدرس نداشت یا وجود نداشت ===== #
        if not user_id or not address_id:
            raise ValidationError("شناسه کاربر و آدرس الزامی است.")
        # ===== در صورت نبود لیست آیتم ===== #
        if not items_data:
            raise ValidationError("لیست آیتم‌ها نمی‌تواند خالی باشد.")
        # ===== دریافت آدرس و اعتبارسنجی ===== #
        try:
            order = self.order_domain.create_order_direct(
                user_id=user_id,
                address_id=address_id,
                items_data=items_data,
                total_price_override=total_price_override
            )
            # ===== اگر توضیحات وجود داشت ===== #
            if 'description' in data:
                    order.description = data['description']
                    order.save(update_fields=['description'])

            logger.info(f"Custom Order {order.id} created successfully.")
            return order

        except Exception as e:
            logger.error(f"Failed to create custom order: {e}")
            raise e
    
    # ============ UPDATE ORDER ============ #
    @transaction.atomic
    def update_order_details(self, admin_user: User, order_id: int, data: Dict[str, Any]) -> Order:
        """
        ویرایش اطلاعات کلی سفارش (آدرس، نوع، قیمت کل، توضیحات).
        """
        order = get_object_or_404(Order, pk=order_id)
        # ===== آدرس ===== #
        if 'address_id' in data:
            address = get_object_or_404(Address, pk=data['address_id'])
            if address.user_id != order.user_id:
                logger.warning(f"Admin assigned address {address.id} to user {order.user_id} (Mismatch)")
            order.address = address

        # ===== نوع سفارش ===== #
        if 'type' in data:
            order.type = data['type']

        # ===== توضیحات ===== #
        if 'description' in data:
            order.description = data['description']

        # ===== تغییر قیمت کل ===== #
        if 'total_price' in data:
            new_price = Decimal(str(data['total_price']))
            order.total_price = new_price

        order.save()
        logger.info(f"Order {order_id} updated by Admin {admin_user.id}")
        return order

    # ========== DELETE ========== #
    def delete_order(self, order_id: int):
        """
        حذف یک سفارشات براساس شناسه آن
        """
        try:
            Order.objects.filter(pk=order_id).delete()
        except Exception as e:
            raise (f"خطا در حذف سفارش: {str(e)}")
    
    # ============ BULK ACTIONS ============ #
    def bulk_delete_orders(self, order_ids: List[int]):
        """
        حذف گروهی سفارشات (فقط سفارشات لغو شده یا پیش‌نویس).
        """
        # ===== دریافت سفارشات ===== #
        return self.order_domain.bulk_delete_orders(order_ids)
    
    def bulk_change_status(self, order_ids: List[int], new_status_id: int):
        """
        تغییر وضعیت گروهی.
        برای این سیستم ممکن هست که این قسمت اصلا نیازی نباشه و به کار نیاد.
        """
        status = OrderStatus.objects.get(id=new_status_id)
        updated_count = Order.objects.filter(id__in=order_ids).update(current_status=status)
        return updated_count
    