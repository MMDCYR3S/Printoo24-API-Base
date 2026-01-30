import logging
from typing import List, Dict, Any
from decimal import Decimal

from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core.exceptions import ValidationError

from core.models import User, Order, OrderStatus, Address
from core.order.services import OrderService

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
            .order_by('-created_at').filter(type="2")

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
        recipient_name = data.get('recipient_name')
        recipient_phone = data.get('recipient_phone')
        company_name = data.get('company_name')
        full_address = data.get('full_address')
        items_data = data.get('items', [])
        total_price_override = data.get('price')
        # ===== اگر کاربر آدرس نداشت یا وجود نداشت ===== #
        if not user_id and not recipient_name:
                raise ValidationError("یا شناسه کاربر را از بین مشتریان انتخاب کنید و یا یک نام برای اون انتخاب کنید.")
        if not address_id and not full_address:
            raise ValidationError("باید آدرس را انتخاب یا وارد کنید")
        # ===== در صورت نبود لیست آیتم ===== #
        if not items_data:
            raise ValidationError("لیست آیتم‌ها نمی‌تواند خالی باشد.")
        # ===== دریافت آدرس و اعتبارسنجی ===== #
        try:
            order = self.order_domain.create_order_direct(
                user_id=user_id,
                address_id=address_id,
                recipient_name=recipient_name,
                recipient_phone=recipient_phone,
                company_name=company_name,
                full_address=full_address,
                items_data=items_data,
                total_price_override=total_price_override
            )

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
        if 'full_address' in data:
            order.full_address = data['full_address']

        # ===== نوع سفارش ===== #
        if 'type' in data:
            order.type = data['type']

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
    