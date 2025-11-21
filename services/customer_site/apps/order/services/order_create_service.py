import os

from decimal import Decimal
from django.db import transaction
from django.core.files.base import ContentFile
from django.conf import settings

from ..exceptions import (
    EmptyCartError,
    OrderCreationError,
    InsufficientFundsError
)
from core.models import User, OrderStatus, Address, City, Province
from core.common.wallet import WalletService
from core.common.cart import CartRepository, CartItemRepository
from core.common.order import (
    OrderRepository,
    OrderItemRepository,
    DesignFileRepository,
    OrderItemDesignFileRepository,
)

class CreateOrderFromCartService:
    """
    سرویس هماهنگ‌کننده برای ایجاد سفارش از سبد خرید.
    این سرویس قوانین کسب‌وکار را اجرا می‌کند:
    1. بررسی موجودی کیف پول.
    2. ایجاد سفارش به صورت اتمیک (شامل کسر از کیف پول و انتقال فایل‌ها).
    """
    
    def __init__(self):
        # ===== تزریق وابستگی ===== #
        self._cart_repo = CartRepository()
        self._cart_item_repo = CartItemRepository()
        self._order_repo = OrderRepository()
        self._order_item_repo = OrderItemRepository()
        self._design_file_repo = DesignFileRepository()
        self._order_item_design_file_repo = OrderItemDesignFileRepository()
        self._wallet_service = WalletService()
        
    def execute(self, user: User, address: Address | None):
        """
        نقطه ورود اصلی برای اجرای فرآیند ایجاد سفارش.
        """
        cart = self._cart_repo.get_or_create_cart(user)
        cart_items = self._cart_item_repo.get_items_by_cart(cart)
        
        if not cart_items:
            raise EmptyCartError("سبد خرید شما خالی است.")
        
        # ===== محاسبه قیمت کل ===== #
        total_price = sum(item.price * item.quantity for item in cart_items)
        
        # ===== بررسی موجودی کیف پول مشتری ===== #
        user_balance = self._wallet_service.get_user_balance(user)
        if user_balance < total_price:
            raise InsufficientFundsError(f"موجودی شما {user_balance} است، اما هزینه سفارش {total_price} می‌باشد.")
        
        # ===== ایجاد سفارش ===== #
        try:
            with transaction.atomic():
                # ===== ایجاد سفارش مورد نظر براساس اطلاعات سبد خرید ===== #
                initial_status = OrderStatus.objects.get(pk=1) 
                order = self._order_repo.create_order(
                    user=user,
                    order_status=initial_status,
                    address=address if address else None,
                    total_price=total_price,
                    order_type="1"
                )
                # ===== انتقال آیتم های سبد خرید به آیتم های سفارش ===== #
                for cart_item in cart_items:
                    order_item = self._order_item_repo.create_order_item(
                        order=order,
                        product=cart_item.product,
                        price=cart_item.price,
                        quantity=cart_item.quantity,
                        items=cart_item.items
                    )
                    
                # ===== انتقال فایل های آپلود شده ===== #
                for upload in cart_item.uploads.all():
                    # ===== کپی کردن آدرس ===== #
                    source_path = upload.file.path
                    file_name = os.path.basename(source_path)

                    # ===== ایجاد مسیر جدید برای فایل های سفارش ===== #
                    new_relative_path = f'orders/designs/{order.id}/{order_item.id}/{file_name}'
                    new_full_path = os.path.join(settings.MEDIA_ROOT, new_relative_path)
                    os.makedirs(os.path.dirname(new_full_path), exist_ok=True)
                    
                    with open(source_path, 'rb') as source_file:
                        file_content = source_file.read()
                    
                    with open(new_full_path, 'wb') as dest_file:
                            dest_file.write(file_content)
                            
                    design_file = self._design_file_repo.create_design_file(file_path=new_relative_path)
                    # ===== ثبت فایل های طراحی ===== #
                    self._order_item_design_file_repo.add_design_file_to_order(
                        order_item=order_item,
                        file_path=design_file,
                        user=user 
                    )
                    
                # ===== ایجاد تراکنش کسر وجه ===== #
                self._wallet_service.debit(user, total_price, transaction_type="6")
                # ===== حذف آیتم های سبد خرید ===== #
                self._cart_item_repo.delete_items_by_cart(cart)
                
            return order
        
        except Exception as e:
            print(f"Order creation failed: {e}")
            raise OrderCreationError("خطا در هنگام ثبت سفارش. لطفاً دوباره تلاش کنید.") from e
        