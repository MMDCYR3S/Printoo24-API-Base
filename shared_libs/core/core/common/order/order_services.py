from typing import Optional, Dict, Any, List
from django.db.models import Prefetch

from core.models import User, Order, OrderItem, OrderItemDesignFile, OrderStatus, Address
from .order_repo import (
    OrderRepository,
    OrderItemRepository,
    OrderItemDesignFileRepository
)

# ====== Order Service ====== #
class OrderService:
    """
    سرویس مربوط به منطق سفارشات
    """
    
    def __init__(self, repository: OrderRepository):
        self._repository = repository or OrderRepository()

    def create_order(self, user: User, order_status: OrderStatus, address:Address, total_price: float, order_type: str):
        """
        منطق ایجاد سفارش
        """
        order_data = {
            "user": user,
            "order_status": order_status,
            "address": address,
            "total_price": total_price,
            "type": order_type
        }
        
        return self._repository.create_order(order_data)
    
    def get_order_by_id(self, order_id: int) -> Optional[Order]:
        """
        دریافت سفارش با شناسه
        """
        return self._repository.get_order_by_id(order_id)
    
    def get_order_by_user(self, user: User) -> List[Order]:
        """
        دریافت سفارشات یک کاربر
        """
        return self._repository.get_order_by_user(user)

    def get_user_orders_summary(self, user_id: int) -> List[Order]:
        """
        دریافت سفارشات کاربر به همراه تمام جزئیات (آیتم‌ها، محصول، وضعیت، آدرس و فایل‌های طراحی)
        به صورت بهینه شده (Eager Loading).
        """
        return self._repository.get_user_orders_summary(user_id)

# ====== Order Item Service ====== #
class OrderItemService:    
    """
    سرویس برای منطق آیتم های سفارش
    """

    def __init__(self, repository: OrderItemRepository):
        self._repository = repository or OrderItemRepository()
        
    def create_order_item(self, order: Order, product: Any, price: float, quantity: int, items: Dict[str, Any]):
        """
        ایجاد آیتم سفارش
        """
        order_item_data = {
            "order": order,
            "product": product,
            "price": price,
            "quantity": quantity,
            "items": items
        }
        return self._repository.create_order_item(order_item_data)
    
    def get_user_order_item_details(self, user_id: int, order_id: int) -> Optional[OrderItem]:
        """
        دریافت جزئیات آیتم سفارش کاربر
        """
        # ===== دریافت فایل های طراحی هر آیتم سفارش ===== #
        design_files_prefetch = Prefetch(
            'order_item_design_file_order_item',
            queryset=OrderItemDesignFile.objects.select_related('file')
        )
        # ===== دریافت جزئیات آیتم سفارش + فایل های آن ===== #
        items_prefetch = Prefetch(
            'order_item_order',
            queryset=OrderItem.objects.select_related('product').prefetch_related(design_files_prefetch)
        )
        return self._repository.get_order_detail_by_id(user_id, order_id, items_prefetch)
    
# ======== Order Item Design File Service ======== #
class OrderItemDesignFileService:
    """
    سرویس برای منطق فایل های طراحی
    """
    
    def __init__(self, repository: OrderItemDesignFileRepository):
        self._repository = repository or OrderItemDesignFileRepository()
        
    def add_file_to_order_item(self,user: User, order_item: OrderItem, file_path: str) -> OrderItemDesignFile:
        """
        ایجاد یک فایل طراحی برای یک آیتم سفارش
        """
        design_data = {
            "user": user,
            "order_item": order_item,
            "file": file_path
        }
        return self._repository.add_design_file_to_order(design_data)


