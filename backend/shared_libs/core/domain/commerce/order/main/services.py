import uuid
from typing import Optional, List
from django.db import transaction
from django.core.files.base import ContentFile
from core.models import User, Order, OrderItem, OrderStatus, OrderItemFile, Address, OrderCostSheet
from core.domain.commerce.cart import CartRepository
from .repositories import OrderRepository, OrderItemRepository, OrderItemFileRepository

class OrderDomainService:
    def __init__(self):
        self._order_repo = OrderRepository()
        self._item_repo = OrderItemRepository()
        self._cart_repo = CartRepository()
        self._file_repo = OrderItemFileRepository()

    def _generate_order_code(self) -> str:
        return uuid.uuid4().hex[:8].upper()

    @transaction.atomic
    def checkout_cart(self, user: User, address: Address, order_type: str) -> Order:
        """ تبدیل سبد خرید به سفارش نهایی """
        
        # 1. دریافت و اعتبار سنجی سبد
        cart = self._cart_repo.get_cart_by_user(user)
        if not cart or not cart.cart_items.exists():
            raise ValueError("سبد خرید شما خالی است.")

        cart_items = cart.cart_items.select_related('product').prefetch_related('uploads').all()
        base_price = sum(item.price for item in cart_items)

        # 2. وضعیت اولیه
        initial_status, _ = OrderStatus.objects.get_or_create(
            internal_code="PENDING",
            defaults={'name': "در حال بررسی"}
        )
        
        # 3. ایجاد سفارش
        order = self._order_repo.create_order(
            user=user,
            order_status=initial_status,
            address=address,
            total_price=base_price,
            base_price=base_price,
            order_type=order_type,
            order_code=self._generate_order_code()
        )
        
        # 4. ایجاد سند مالی مادر (Cost Sheet) - حیاتی
        OrderCostSheet.objects.create(order=order)

        # 5. انتقال آیتم‌ها و فایل‌ها
        for c_item in cart_items:
            order_item = self._item_repo.create({
                "order": order,
                "product": c_item.product,
                "quantity": c_item.quantity,
                "price": c_item.price,
                "items": c_item.items 
            })

            for upload in c_item.uploads.all():
                if upload.file:
                    new_file_content = ContentFile(upload.file.read())
                    new_file_content.name = upload.file.name.split('/')[-1]
                    
                    self._file_repo.create({
                        "order_item": order_item,
                        "requirement": upload.requirement,
                        "file": new_file_content,
                        "version": 1,
                        "is_latest": True
                    })

        # 6. حذف سبد خرید
        cart.delete()
        return order

    def get_order_details(self, user_id: int, order_id: int) -> Order:
        order = self._order_repo.get_order_with_items(user_id, order_id)
        if not order:
            raise ValueError("سفارش یافت نشد") 
        return order

    def get_user_orders_summary(self, user_id: int) -> List[Order]:
        return self._order_repo.get_user_orders_summary(user_id)