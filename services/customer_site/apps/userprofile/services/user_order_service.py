import logging
from typing import List, Optional

from django.core.exceptions import ValidationError

from core.models import Order
from core.common.order import (
    OrderRepository,
    OrderService,
)

# ===== تعریف لاگر اختصاصی با پیشوند userprofile ===== #
logger = logging.getLogger('userprofile.services.orders')

# ===== User Order List Service ===== #
class UserOrderListService:
    """
    سرویس مدیریت نمایش سابقه سفارشات کاربر.
    
    این سرویس لیست خلاصه‌ای از سفارش‌های گذشته کاربر را
    جهت نمایش در پنل کاربری فراهم می‌کند.
    """
    
    def __init__(self):
        # ===== تزریق وابستگی‌ها ===== #
        self._repo = OrderRepository()
        self._service = OrderService(repository=self._repo)

    def get_user_orders(self, user_id: int) -> List:
        """
        دریافت لیست کلی سفارشات کاربر.

        Args:
            user_id (int): شناسه کاربر.

        Returns:
            List: لیست آبجکت‌های سفارش یا دیکشنری‌های خلاصه.
        """
        logger.info(f"Fetching order history for User ID: {user_id}")
        
        try:
            orders = self._service.get_user_orders_summary(user_id)
            count = len(orders) if isinstance(orders, list) else orders.count()
            logger.info(f"Found {count} orders for User ID: {user_id}")
            return orders
        except Exception as e:
            logger.exception(f"Error fetching order list for User ID: {user_id}")
            raise e

# ===== User Order Detail Service ===== #
class UserOrderDetailService:
    """
    سرویس مدیریت نمایش جزئیات دقیق یک سفارش خاص.
    """
    
    def __init__(self):
        # ===== تزریق وابستگی‌ها ===== #
        self._repo = OrderRepository()
        self._service = OrderService(repository=self._repo)

    def get_order_detail(self, user_id: int, order_id: int) -> Optional[Order]:
        """
        دریافت جزئیات کامل یک سفارش با بررسی مالکیت.

        Args:
            user_id (int): شناسه کاربر.
            order_id (int): شناسه سفارش.

        Returns:
            Order: آبجکت کامل سفارش به همراه آیتم‌ها.

        Raises:
            ValidationError: اگر سفارش پیدا نشود یا متعلق به کاربر نباشد.
        """
        logger.info(f"Fetching details for Order ID: {order_id}, User ID: {user_id}")
        
        try:
            order = self._service.get_user_order_item_details(user_id, order_id)
            
            if not order:
                logger.warning(f"Order ID {order_id} not found or access denied for User ID: {user_id}")
                raise ValidationError("سفارش مورد نظر یافت نشد یا متعلق به شما نیست.")
            
            logger.debug(f"Order details retrieved successfully for Order ID: {order_id}")
            return order
            
        except ValidationError as e:
            raise e
        except Exception as e:
            logger.exception(f"Unexpected error retrieving order {order_id} for User ID: {user_id}")
            raise e
