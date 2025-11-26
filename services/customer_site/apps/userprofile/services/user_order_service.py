from typing import List, Optional
from core.common.order import (
    OrderRepository,
    OrderService,
    OrderItemRepository,
    OrderItemService,
)
from django.core.exceptions import ValidationError
from core.models import Order

# ===== User Order List Service ===== #
class UserOrderListService:
    """
    سرویس برای نمایش سابقه سفارشات کاربر
    """
    def __init__(self):
        self._repo = OrderRepository()
        self._servcie = OrderService(repository=OrderRepository())

    def get_user_orders(self, user_id: int) -> List:
        """لیست کلی سفارشات کاربر"""
        return self._servcie.get_user_orders_summary(user_id)

# ===== User Order Detail Service ===== #
class UserOrderDetailService:
    """
    سرویس برای نمایش جزئیات سابقه هر سفارش کاربر
    """
    def __init__(self):
        self._repo = OrderRepository()
        self._servcie = OrderService(repository=OrderRepository())

    def get_order_detail(self, user_id: int, order_id: int) -> Optional[Order]:
        """دریافت جزئیات کامل یک سفارش"""
        order = self._servcie.get_user_order_item_details(user_id, order_id)
        if not order:
            raise ValidationError("سفارش مورد نظر یافت نشد یا متعلق به شما نیست.")
        return order
