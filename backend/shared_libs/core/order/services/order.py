import uuid
from typing import List, Dict, Optional
from django.db import transaction
from django.db.models import Q
from django.core.files.base import ContentFile

from core.order.models import Order, OrderItem, OrderItemFile, OrderStatus, OrderCostSheet
from core.models import User, Address, Invoice
from cart.models import Cart

from ..exceptions import OrderNotFoundException

# ========== ORDER SERVICE ========== #
class OrderService:
    """
    سرویس دامنه مدیریت سفارشات (Checkout, Operations)
    """

    def _generate_order_code(self) -> str:
        return uuid.uuid4().hex[:8].upper()

    def get_order_details(self, user_id: int, order_id: int) -> Order:
        """
        دریافت جزئیات سفارش برای کاربر.
        """
        order = Order.objects.get_order_with_items(user_id, order_id)
        if not order:
            raise OrderNotFoundException("سفارش یافت نشد") 
        return order

    def get_user_orders_summary(self, user_id: int) -> List[Order]:
        user = User.objects.get(id=user_id) 
        return Order.objects.get_user_orders_summary(user)
    
    @transaction.atomic
    def bulk_delete_orders(self, order_ids: List[int]) -> Dict[str, int]:
        """
        حذف گروهی هوشمند سفارشات.
        قانون 1: فقط سفارشاتی که وضعیتشان اجازه حذف می‌دهد.
        قانون 2: سفارشاتی که فاکتور نهایی شده یا پرداخت کامل دارند، حذف نمی‌شوند.
        """
        deletable_types = ['initial', 'cancel', 'pending']
        
        # فیلتر اولیه بر اساس وضعیت
        orders_to_delete = Order.objects.filter(
            id__in=order_ids,
            current_status__status_type__in=deletable_types
        )

        orders_to_delete = orders_to_delete.exclude(
            Q(invoice__status='finalize') |
            Q(invoice__status='paid_full') |
            Q(invoice__status='paid_partial')
        )

        count_to_delete = orders_to_delete.count()
        deleted_ids = list(orders_to_delete.values_list('id', flat=True))
        
        if 'Invoice' in globals() or 'Invoice' in locals():
             Invoice.objects.filter(order__in=orders_to_delete).delete()

        orders_to_delete.delete()
        
        return {
            "requested_count": len(order_ids),
            "deleted_count": count_to_delete,
            "skipped_count": len(order_ids) - count_to_delete,
            "deleted_ids": deleted_ids,
            "message": f"{count_to_delete} سفارش با موفقیت حذف شدند."
        }
