from typing import Optional, Dict, Any, List

from core.models import User, Order, OrderItem, OrderItemDesignFile, DesignFile, OrderStatus
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

    def create_order(self, user: User, order_status: OrderStatus, total_price: float, order_type: str):
        """
        منطق ایجاد سفارش
        """
        order_data = {
            "user": user,
            "order_status": order_status,
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
