import logging
from typing import List, Optional, Any
from rest_framework.exceptions import NotFound # بهتر است از اکسپشن DRF استفاده کنیم

from core.models import Order
from core.domain.commerce.order import OrderDomainService

logger = logging.getLogger('userprofile.services.orders')

class UserOrderListService:
    """
    سرویس اپلیکیشن برای مدیریت سفارشات در پنل کاربر.
    """
    
    def __init__(self):
        # استفاده از دامین سرویس به جای ریپازیتوری مستقیم (معماری تمیزتر)
        self._domain_service = OrderDomainService()

    def get_user_orders(self, user_id: int) -> List[Order]:
        """
        دریافت لیست خلاصه سفارشات.
        """
        logger.info(f"Fetching order history for User ID: {user_id}")
        try:
            # فراخوانی متد دامین سرویس که لیست خلاصه (بدون آیتم) برمی‌گرداند
            orders = self._domain_service.get_user_orders_summary(user_id)
            return orders
        except Exception as e:
            logger.error(f"Error fetching orders: {e}")
            raise e

    def get_order_detail(self, user_id: int, order_id: int) -> Order:
        """
        دریافت جزئیات کامل سفارش تکی.
        """
        logger.info(f"Fetching detail Order {order_id} for User {user_id}")
        
        try:
            # فراخوانی متد دامین سرویس که شامل Prefetch فایل‌ها و آیتم‌هاست
            order = self._domain_service.get_user_order_item_details(user_id, order_id)
            
            if not order:
                logger.warning(f"Order {order_id} not found for user {user_id}")
                raise NotFound("سفارش مورد نظر یافت نشد.")
            
            return order
            
        except Exception as e:
            logger.error(f"Error fetching order detail: {e}")
            raise e
