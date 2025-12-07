from typing import List, Optional
from django.db.models import Prefetch, QuerySet
from core.utils.base_repository import BaseRepository
from core.models import (
    Order, OrderItem, OrderItemFile, OrderStatus, Address, User,
    OrderStateLog, OrderCostItem, OrderShipment
)

class OrderRepository(BaseRepository[Order]):
    def __init__(self):
        super().__init__(Order)
    
    # ===== منطق سمت مشتری ===== #
    def get_order_by_id(self, order_id: int) -> Optional[Order]:
        return self.get_by_id(order_id)
    
    def get_order_by_user(self, user: User) -> List[Order]:
        return self.filter(user=user)
    
    def get_user_orders_summary(self, user: User) -> QuerySet[Order]:
        """فقط خلاصه سفارشات"""
        return self.model.objects.filter(user=user)\
            .select_related('current_status')\
            .order_by('-created_at')
    
    def create_order(self, user: User, order_status: OrderStatus, address: Address, 
                     total_price: float, order_type: str, order_code: str, base_price: float): 
        return self.create({
            "user": user,
            "current_status": order_status,
            "address": address,
            "total_price": total_price,
            "base_products_price": base_price,
            "type": order_type,
            "order_code": order_code
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
    
    # ===== سمت ادمین - بخش مدیریت داخلی ===== #
    def get_full_order_detail_for_admin(self, order_id: int) -> Optional[Order]:
        """
        
        دریافت سوپر-دیتا برای پنل مدیریت (شامل لاگ‌ها، هزینه‌ها، فایل‌ها و...)
        """
        return self.model.objects.select_related(
            'user', 'current_status', 'address', 'invoice_order'
        ).prefetch_related(
            # ===== آیتم های سفارش و فایل های طراحی ===== #
            Prefetch(
                'items',
                queryset=OrderItem.objects.select_related('product').prefetch_related(
                    Prefetch('files', queryset=OrderItemFile.objects.select_related('requirement__spec').order_by('-version'))
                )
            ),
            # ===== وضعیت سفارش ===== #
            Prefetch('state_logs', queryset=OrderStateLog.objects.select_related('user', 'from_status', 'to_status').order_by('-timestamp')),
            # ===== هزینه های شناور مربوط به سفارش ===== #
            Prefetch('costs', queryset=OrderCostItem.objects.select_related('cost_type', 'created_by')),
            # ===== مرسوله های مربوط به سفارش ===== #
            Prefetch('shipments', queryset=OrderShipment.objects.select_related('delivery_method'))
        ).filter(id=order_id).first()

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
