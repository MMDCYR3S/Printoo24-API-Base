from typing import List, Any, Dict, Optional

from django.db.models import Prefetch, QuerySet

from core.utils import BaseRepository
from core.models import Order, OrderItem, OrderItemDesignFile, DesignFile, OrderStatus, Address, User

# ======= Order Repository ======= #
class OrderRepository(BaseRepository[Order]):
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
    
    def get_order_by_user(self, user: User) -> List[Order]:
        """
        دریافت سفارشات یک کاربر
        """
        return self.filter(user=user)
    
    def get_user_orders_summary(self, user: User) -> QuerySet[Order]:
        """فقط سفارشات را به همراه وضعیت، کل مبلغ و زمان نمایش می‌دهد؛ بدون آیتم‌ها"""
        return self.model.objects.filter(user=user)\
            .select_related('order_status')\
            .order_by('-created_at')
    
    def create_order(self, user: User, order_status: OrderStatus, address: Address, total_price: float, order_type: str):
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
    
    def get_order_with_items(self, user_id: int, order_id: int) -> Optional[Order]:
        """دریافت جزئیات کامل یک سفارش خاص برای کاربر"""
        
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
        
        return self.model.objects.filter(id=order_id, user_id=user_id)\
            .select_related('order_status', 'address')\
            .prefetch_related(items_prefetch)\
            .first()

# ======= Order Item Repository ======= #
class OrderItemRepository(BaseRepository[OrderItem]):
    """
    مخزن انتزاعی برای آیتم های سفارشات
    """
    def __init__(self):
        super().__init__(OrderItem)

# ========= Order Item Design File Repository ======== #
class OrderItemDesignFileRepository(BaseRepository[OrderItemDesignFile]):
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
class DesignFileRepository(BaseRepository[DesignFile]):
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
