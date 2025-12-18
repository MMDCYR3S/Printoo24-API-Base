import uuid
from typing import List, Dict
from django.db import transaction
from django.db.models import Q
from django.core.files.base import ContentFile
from core.models import User, Order, OrderStatus, Address, OrderCostSheet, Invoice
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
    
    @transaction.atomic
    def bulk_delete_orders(self, order_ids: List[int]) -> Dict[str, int]:
        """
        حذف گروهی هوشمند سفارشات.
        قانون 1: فقط سفارشاتی که وضعیتشان اجازه حذف می‌دهد (مثلاً در حال بررسی یا لغو شده) حذف می‌شوند.
        قانون 2: سفارشاتی که فاکتور نهایی شده یا پرداخت کامل دارند، به هیچ وجه حذف نمی‌شوند.
        """
        deletable_types = ['initial', 'cancel', 'pending']
        orders_to_delete = Order.objects.filter(
            id__in=order_ids,
            current_status__status_type__in=deletable_types
        )

        orders_to_delete = orders_to_delete.exclude(
            Q(invoice__status=Invoice.Status.FINALIZE) | 
            Q(invoice__status=Invoice.Status.PAID_FULL) |
            Q(invoice__status=Invoice.Status.PAID_PARTIAL)
        )

        count_to_delete = orders_to_delete.count()
        deleted_ids = list(orders_to_delete.values_list('id', flat=True))
        
        Invoice.objects.filter(order__in=orders_to_delete).delete()

        orders_to_delete.delete()
        
        return {
            "requested_count": len(order_ids),
            "deleted_count": count_to_delete,
            "skipped_count": len(order_ids) - count_to_delete,
            "deleted_ids": deleted_ids,
            "message": f"{count_to_delete} سفارش با موفقیت حذف شدند."
        }