# در فایل apps/dashboard/services/order_service.py

from django.core.exceptions import ValidationError
from core.models import Order, OrderStatus, Address
from core.order.services import OrderService
class OrderDashboardService:
    def __init__(self):
        self.domain = OrderService()

    def get_order_list(self):
        return Order.objects.get_all_orders_summary()

    def get_order_detail(self, order_id):
        return self.domain.get_order_by_id(order_id)
        
    def get_order_statuses(self):
        """ واکشی لیست تمام وضعیت‌ها برای نمایش در دراپ‌داون فرانت‌اند """
        return OrderStatus.objects.all().select_related('group').order_by('sort_order')

    def create_order(self, data):
        return self.domain.create_order_direct(**data)

    def update_order(self, order_id, data):
        return self.domain.update_order_details(order_id, data)

    def change_status(self, order_id, internal_code, actor, description=""):
        return self.domain.change_order_status(order_id, internal_code, actor, description)

    def delete_order(self, order_id):
        # اول بررسی وجود سفارش
        if not Order.objects.filter(id=order_id).exists():
            raise Exception(f"سفارش با شناسه {order_id} یافت نشد.")

        result = self.domain.bulk_delete_orders([order_id])
        return result


    def bulk_delete(self, order_ids):
        return self.domain.bulk_delete_orders(order_ids)

    def bulk_change_status(self, order_ids, internal_code, actor):
        return self.domain.bulk_change_status(order_ids, internal_code, actor)
    
    def get_user_addresses(self, user_id):
        return Address.objects.filter(user_id=user_id)
