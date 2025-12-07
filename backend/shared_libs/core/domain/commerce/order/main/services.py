import uuid
from typing import Optional, List
from django.db import transaction
from django.core.files.base import ContentFile
from core.models import User, Order, OrderItem, OrderStatus, OrderItemFile, Address
from core.domain.commerce.cart import CartRepository
from .repositories import OrderRepository, OrderItemRepository, OrderItemFileRepository

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
        self._file_repo = OrderItemFileRepository()

    def _generate_order_code(self) -> str:
        """ تولید کد پیگیری یکتا (8 کاراکتر) """
        return uuid.uuid4().hex[:8].upper()

    # ==== عملیات نهایی تبدیل سبد خرید به سفارش ===== #
    @transaction.atomic
    def checkout_cart(self, user: User, address: Address, order_type: str) -> Order:
        """ تبدیل سبد خرید به سفارش نهایی """
        
        # ===== دریافت سبد خرید ==== #
        cart = self._cart_repo.get_cart_by_user(user)
        if not cart or not cart.cart_items.exists():
            raise ValueError("سبد خرید شما خالی است.")

        cart_items = cart.cart_items.select_related('product').prefetch_related('uploads').all()

        # ===== محاسبه قیمت کل ===== #
        base_price = sum(item.price for item in cart_items)

        # ===== ایجاد سفارش ===== #
        initial_status, _ = OrderStatus.objects.get_or_create(
            name="در حال بررسی",
            internal_code="PENDING"
            )
        
        # ===== ایجاد سفارش =====
        order = self._order_repo.create_order(
            user=user,
            order_status=initial_status,
            address=address,
            total_price=base_price,
            base_price=base_price,
            order_type=order_type,
            order_code=self._generate_order_code()
        )
        
        # ===== ایجاد آیتم‌های سفارش ===== #
        for c_item in cart_items:
            order_item = self._item_repo.create({
                "order": order,
                "product": c_item.product,
                "quantity": c_item.quantity,
                "unit_price": c_item.product.pricing_config.price,
                "price": c_item.price,
                "items": c_item.items 
            })

            # ===== انتقال فایل‌های طراحی (نسخه بندی شده) ===== #
            for upload in c_item.uploads.all():
                if upload.file:
                    new_file_content = ContentFile(upload.file.read())
                    new_file_content.name = upload.file.name.split('/')[-1]
                    
                    OrderItemFile.objects.create(
                        order_item=order_item,
                        requirement=upload.requirement,
                        file=new_file_content,
                        version=1,
                        is_latest=True
                    )
        # ===== پاک کردن سبد خرید ===== #
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
        return self._order_repo.get_order_by_id(order_id)
    
    def get_order_by_user(self, user: User) -> List[Order]:
        """
        دریافت سفارشات یک کاربر
        """
        return self._order_repo.get_order_by_user(user)

    def get_user_orders_summary(self, user_id: int) -> List[Order]:
        """
        دریافت سفارشات کاربر به همراه تمام جزئیات (آیتم‌ها، محصول، وضعیت، آدرس و فایل‌های طراحی)
        به صورت بهینه شده (Eager Loading).
        """
        return self._order_repo.get_user_orders_summary(user_id)

    def get_user_order_item_details(self, user_id: int, order_id: int) -> Optional[Order]:
        """
        دریافت جزئیات آیتم سفارش کاربر
        """
        return self._order_repo.get_order_with_items(user_id, order_id)
