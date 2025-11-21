from typing import List, Any, Generic, Dict, Optional, TypeVar

from core.common.repositories import IRepository
from core.models import Order, OrderItem, OrderItemDesignFile, DesignFile, OrderStatus, Address

# ======= Order Repository ======= #
class OrderRepository(IRepository[Order]):
    """
    مخزن انتزاعی برای سفارشات
    """
    
    def __init__(self):
        super().__init__(Order)
    
    def get_order_by_id(self, order_id: int) -> Optional[Order]:
        """
       دریافت سفارش با شناسه خاص آن 
        """
        return self.get_by_id(order_id)
    
    def get_order_by_user(self, user: Any) -> List[Order]:
        """
        دریافت سفارشات یک کاربر
        """
        return self.filter(user=user)
    
    def create_order(self, user: Any, order_status: OrderStatus, address: Address, total_price: float, order_type: str):
        """
        ساخت یک سفارش بدون آیتم های آن
        """
        order_data = {
            "user": user,
            "order_status": order_status,
            "address": address,
            "total_price": total_price,
            "type": order_type
        }
        return self.create(order_data)

# ======= Order Item Repository ======= #
class OrderItemRepository(IRepository[OrderItem]):
    """
    مخزن انتزاعی برای آیتم های سفارشات
    """
    def __init__(self):
        super().__init__(OrderItem)
    
    def create_order_item(self, order: Order, product: Any, price: float, quantity: int, items: Dict[str, Any]):
        """
        ساخت یک آیتم سفارش برای سفارش مورد نظر
        """
        order_item_data = {
            "order": order,
            "product": product,
            "price": price,
            "quantity": quantity,
            "items": items
        }
        
        return self.create(order_item_data)

# ========= Order Item Design File Repository ======== #
class OrderItemDesignFileRepository(IRepository[OrderItemDesignFile]):
    """
    مخزن انتزاعی برای فایل های طراحی سفارشات
    """
    def __init__(self):
        super().__init__(OrderItemDesignFile)
    
    def add_design_file_to_order(self, user: Any, order_item:OrderItem, file_path: str) -> DesignFile:
        """
        یک رکورد فایل طراحی جدید ایجاد می‌کند.
        فایل فیزیکی باید قبلاً کپی شده باشد.
        """
        data = {
            "user": user,
            "order_item": order_item,
            "file": file_path
        }
        return self.create(data)

# ======== Design File Repository ======== #
class DesignFileRepository(IRepository[DesignFile]):
    """
    مخزن انتزاعی برای فایل‌های طراحی
    """
    def __init__(self):
        super().__init__(DesignFile)

    def create_design_file(self, file_path: str) -> DesignFile:
        """
        یک رکورد فایل طراحی جدید ایجاد می‌کند.
        فایل فیزیکی باید قبلاً کپی شده باشد.
        """
        data = {"file": file_path}
        return self.create(data)
