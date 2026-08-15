import logging
from typing import List
from rest_framework.exceptions import NotFound

from core.models import Order, Quotation
from core.order.services import OrderService
from core.infrastructure.messages import msg_provider

logger = logging.getLogger('userprofile.services.orders')

class UserOrderListService:
    """
    سرویس اپلیکیشن برای مدیریت سفارشات در پنل کاربر.
    """
    
    def __init__(self):
        self._domain_service = OrderService()

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
            order = self._domain_service.get_order_details(user_id, order_id)
            
            if not order:
                logger.warning(f"Order {order_id} not found for user {user_id}")
                raise NotFound(msg_provider.get("profile.E8006"))
            
            return order
            
        except Exception as e:
            logger.error(f"Error fetching order detail: {e}")
            raise e

    def get_order_quotation(self, user_id: int, order_id: int) -> Quotation:
        """
        دریافت پیش‌فاکتور مربوط به یک سفارش خاص برای کاربر.
        """
        quotation = Quotation.objects.get_quotation_by_order(order_id)

        if not quotation:
            logger.warning(f"Quotation not found for order {order_id}")
            raise NotFound(msg_provider.get("profile.E8007"))

        if quotation.converted_order.user_id != user_id:
            logger.warning(f"Security Alert: User {user_id} tried to access quotation of Order {order_id}")
            raise NotFound(msg_provider.get("profile.E8007"))

        return quotation
 
    def get_order_invoice(self, user_id: int, order_id: int):
        from core.financial.models import Invoice 
        
        invoice = Invoice.objects.get_invoice_with_full_details_by_order(order_id, by_order=True)

        if not invoice:
            logger.warning(f"Invoice not found for order {order_id}")
            raise NotFound(msg_provider.get("profile.E8008"))

        if invoice.order.user_id != user_id:
            logger.warning(f"Security Alert: User {user_id} tried to access invoice of Order {order_id}")
            raise NotFound(msg_provider.get("profile.E8008"))
        
        if not invoice.is_paid:
            logger.info(f"Invoice for order {order_id} is not fully paid yet.")
            raise NotFound(msg_provider.get("profile.E8009"))

        return invoice

