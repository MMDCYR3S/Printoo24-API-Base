from typing import Optional, Dict, Any, List
from django.db.models import Prefetch
from django.db import transaction

from core.models import (
    User,
    Order,
    OrderItem,
    OrderStatus,
    OrderItemDesignFile,
    DesignFile,
    Address
)
from core.domain.cart import CartRepository
from .repositories import (
    OrderRepository,
    OrderItemRepository,
    OrderItemDesignFileRepository
)

# ====== Order Domain Service ====== #
class OrderDomainService:
    """
    سرویس مربوط به منطق سفارشات
    """
    
    # ===== سازنده ====== #
    def __init__(self):
            self._order_repo = OrderRepository()
            self._item_repo = OrderItemRepository()
            self._cart_repo = CartRepository()

    # ==== عملیات نهایی تبدیل سبد خرید به سفارش ===== #
    @transaction.atomic
    def checkout_cart(self, user: User, address: Address, order_type: str) -> Order:
        """
        عملیات نهایی تبدیل سبد خرید به سفارش.
        """
        # ===== دریافت سبد خرید فعال کاربر ===== #
        cart = self._cart_repo.get_or_create_cart(user)
        if not cart or not cart.cart_items.exists():
            raise ValueError("سبد خرید خالی است.")
        
        # ===== محاسبه قیمت کل سبد خرید ===== #
        total_price = sum(item.price for item in cart.cart_items.all())
        
        # ===== ایجاد سفارش جدید ===== #
        initial_status = OrderStatus.objects.get(name__in="در انتظار بررسی")
        
        order = self._order_repo.create({
            "user": user,
            "address": address,
            "order_status": initial_status,
            "total_price": total_price,
            "type": order_type
        })
        
        # ===== انتقال آیتم‌های سبد خرید به سفارش ===== #
        cart_items = cart.cart_items.select_related('product').prefetch_related('uploads').all()
        
        for c_item in cart_items:
            order_item = self._item_repo.create({
                "order": order,
                "product": c_item.product,
                "quantity": c_item.quantity,
                "price": c_item.price,
                "items": c_item.items
            })

            # ===== انتقال فایل‌های طراحی مرتبط با آیتم سبد خرید ===== #
            for upload in c_item.uploads.all():
                design_file = DesignFile.objects.create(file=upload.file)
                
                OrderItemDesignFile.objects.create(
                    user=user,
                    order_item=order_item,
                    file=design_file
                )
        # ===== حذف سبد خرید پس از تبدیل به سفارش ===== #
        cart.delete()
        return order
    
    # ===== دریافت جزئیات سفارش ===== #
    def get_order_details(self, user_id: int, order_id: int) -> Order:
        order = self._order_repo.get_order_with_items(user_id, order_id)
        if not order:
            raise ValueError("سفارش یافت نشد") 
        return order
    
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

    def get_user_order_item_details(self, user_id: int, order_id: int) -> Optional[Order]:
        """
        دریافت جزئیات آیتم سفارش کاربر
        """
        return self._repository.get_order_detail_by_id(user_id, order_id)

# # ====== Order Item Service ====== #
# class OrderItemService:    
#     """
#     سرویس برای منطق آیتم های سفارش
#     """

#     def __init__(self, repository: OrderItemRepository):
#         self._repository = repository or OrderItemRepository()
        
#     def create_order_item(self, order: Order, product: Any, price: float, quantity: int, items: Dict[str, Any]):
#         """
#         ایجاد آیتم سفارش
#         """
#         order_item_data = {
#             "order": order,
#             "product": product,
#             "price": price,
#             "quantity": quantity,
#             "items": items
#         }
#         return self._repository.create_order_item(order_item_data)
    
# # ======== Order Item Design File Service ======== #
# class OrderItemDesignFileService:
#     """
#     سرویس برای منطق فایل های طراحی
#     """
    
#     def __init__(self, repository: OrderItemDesignFileRepository):
#         self._repository = repository or OrderItemDesignFileRepository()
        
#     def add_file_to_order_item(self,user: User, order_item: OrderItem, file_path: str) -> OrderItemDesignFile:
#         """
#         ایجاد یک فایل طراحی برای یک آیتم سفارش
#         """
#         design_data = {
#             "user": user,
#             "order_item": order_item,
#             "file": file_path
#         }
#         return self._repository.add_design_file_to_order(design_data)


