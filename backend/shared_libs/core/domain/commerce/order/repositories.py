from typing import List, Any, Optional
from django.db.models import Prefetch, QuerySet
from core.utils import BaseRepository
from core.models import (
    Order, OrderItem, OrderItemFile, OrderStatus, Address, User
)

class OrderRepository(BaseRepository[Order]):
    def __init__(self):
        super().__init__(Order)
    
    def get_order_by_id(self, order_id: int) -> Optional[Order]:
        return self.get_by_id(order_id)
    
    def get_order_by_user(self, user: User) -> List[Order]:
        return self.filter(user=user)
    
    def get_user_orders_summary(self, user: User) -> QuerySet[Order]:
        """فقط خلاصه سفارشات"""
        return self.model.objects.filter(user=user)\
            .select_related('order_status')\
            .order_by('-created_at')
    
    def create_order(self, user: User, order_status: OrderStatus, address: Address, total_price: float, order_type: str):
        return self.create({
            "user": user,
            "order_status": order_status,
            "address": address,
            "total_price": total_price,
            "type": order_type
        })
    
    def get_order_with_items(self, user_id: int, order_id: int) -> Optional[Order]:
        """
        دریافت جزئیات کامل سفارش با ساختار جدید (OrderItemFile).
        """
        # ===== دریافت فایل های سفارش ===== #
        files_prefetch = Prefetch(
            'files',
            queryset=OrderItemFile.objects.select_related('requirement__spec')
        )

        # ===== ایجاد ریلیشن های جدید ===== #
        items_prefetch = Prefetch(
            'order_item_order',
            queryset=OrderItem.objects.select_related('product').prefetch_related(files_prefetch)
        )
        
        return self.model.objects.filter(id=order_id, user_id=user_id)\
            .select_related('order_status', 'address')\
            .prefetch_related(items_prefetch)\
            .first()

# ======= Order Item Repository ======= #
class OrderItemRepository(BaseRepository[OrderItem]):
    def __init__(self):
        super().__init__(OrderItem)

# ======= Order Item File Repository (NEW) ======= #
class OrderItemFileRepository(BaseRepository[OrderItemFile]):
    """
    جایگزین ریپازیتوری‌های قدیمی فایل طراحی.
    """
    def __init__(self):
        super().__init__(OrderItemFile)
