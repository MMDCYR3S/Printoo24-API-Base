# در فایل apps/dashboard/services/order_service.py

from django.core.exceptions import ValidationError
from core.models import Order, OrderStatus, Address
from core.order.services import OrderService
from core.users.services import CustomerService

class OrderDashboardService:
    def __init__(self):
        self.domain = OrderService()
        self.customer_service = CustomerService()

    def get_order_list(self):
        return Order.objects.get_all_orders_summary()

    def get_order_detail(self, order_id):
        return self.domain.get_order_by_id(order_id)
        
    def get_order_statuses(self):
        """ واکشی لیست تمام وضعیت‌ها برای نمایش در دراپ‌داون فرانت‌اند """
        return OrderStatus.objects.all().select_related('group').order_by('sort_order')

    def get_all_customers(self):
        """ دریافت لیست مشتریان برای انتخاب در سفارش دستی """
        return self.customer_service.get_all_customers()

    def create_order(self, data):
        return self.domain.create_order_direct(**data)

    def update_order(self, order_id, data):
        return self.domain.update_order_details(order_id, data)

    def change_status(self, order_id, status_code, actor, description=""):
        return self.domain.change_order_status(order_id, status_code, actor, description)

    def delete_order(self, order_id):
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

    def get_order_item(self, order_item_id: int):
        from core.models import OrderItem
        try:
            return OrderItem.objects.get(id=order_item_id)
        except OrderItem.DoesNotExist:
            raise Exception(f"آیتم سفارش با شناسه {order_item_id} یافت نشد.")

    def upload_order_item_file(self, order_item_id: int, uploaded_file) -> None:
        from apps.dashboard.tasks import upload_order_item_file_task
        import tempfile, os

        self.get_order_item(order_item_id)

        original_filename = uploaded_file.name
        suffix = os.path.splitext(original_filename)[1]

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            for chunk in uploaded_file.chunks():
                tmp.write(chunk)
            temp_path = tmp.name

        upload_order_item_file_task.delay(
            order_item_id=order_item_id,
            temp_file_path=temp_path,
            original_filename=original_filename
        )

    def delete_order_item_file(self, order_item_id: int) -> None:
        from core.models import OrderItemFile
        self.get_order_item(order_item_id)

        files = OrderItemFile.objects.filter(order_item_id=order_item_id)
        for f in files:
            if f.file:
                f.file.delete(save=False)
        f.delete()

    def update_financial_details(self, order_id, data, actor):
        return self.domain.update_financial_details(order_id, data, actor)