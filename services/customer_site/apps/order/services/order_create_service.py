import os
import logging
from decimal import Decimal
from django.db import transaction
from django.conf import settings

from ..exceptions import (
    EmptyCartError,
    OrderCreationError,
    InsufficientFundsError
)
from core.models import User, OrderStatus, Address
from core.common.wallet import WalletService
from core.common.cart import CartRepository, CartItemRepository
from core.common.order import (
    OrderRepository,
    OrderItemRepository,
    DesignFileRepository,
    OrderItemDesignFileRepository,
)

# ===== تعریف لاگر اختصاصی برای این سرویس ===== #
logger = logging.getLogger('shop.services.order_creation')

class CreateOrderFromCartService:
    """
    سرویس مدیریت فرآیند تبدیل سبد خرید به سفارش نهایی.
    
    این کلاس مسئولیت هماهنگی بین سرویس‌های مختلف (کیف پول، فایل‌ها، دیتابیس) را بر عهده دارد
    تا یک سفارش به صورت اتمیک و ایمن ثبت شود.
    
    وظایف اصلی:
    1. اعتبارسنجی سبد خرید (خالی نبودن).
    2. محاسبه قیمت نهایی آیتم‌ها.
    3. بررسی موجودی کیف پول کاربر.
    4. ایجاد رکورد سفارش و آیتم‌های آن در دیتابیس.
    5. انتقال امن فایل‌های طراحی از پوشه موقت به پوشه نهایی سفارش.
    6. کسر وجه از کیف پول و ثبت تراکنش.
    7. پاکسازی سبد خرید پس از ثبت موفق.

    Exceptions:
        EmptyCartError: در صورتی که سبد خرید خالی باشد.
        InsufficientFundsError: در صورتی که موجودی کیف پول کافی نباشد.
        OrderCreationError: در صورت بروز هرگونه خطای سیستمی هنگام ثبت.
    """
    
    def __init__(self):
        # ===== تزریق وابستگی‌های مورد نیاز ===== #
        self._cart_repo = CartRepository()
        self._cart_item_repo = CartItemRepository()
        self._order_repo = OrderRepository()
        self._order_item_repo = OrderItemRepository()
        self._design_file_repo = DesignFileRepository()
        self._order_item_design_file_repo = OrderItemDesignFileRepository()
        self._wallet_service = WalletService()
        
    def execute(self, user: User, address: Address | None):
        """
        اجرای منطق اصلی ثبت سفارش.

        Args:
            user (User): کاربر درخواست‌دهنده سفارش.
            address (Address | None): آدرس ارسال (در صورت فیزیکی بودن محصول).

        Returns:
            Order: آبجکت سفارش ایجاد شده.

        Raises:
            EmptyCartError, InsufficientFundsError, OrderCreationError
        """
        logger.info(f"Starting order creation process for User ID: {user.id}")

        cart = self._cart_repo.get_or_create_cart(user)
        cart_items = self._cart_item_repo.get_items_by_cart(cart)
        
        if not cart_items:
            logger.warning(f"Order creation failed: Cart is empty for User ID: {user.id}")
            raise EmptyCartError("سبد خرید شما خالی است.")
        
        # ===== محاسبه قیمت کل سفارش ===== #
        total_price = sum(item.price * item.quantity for item in cart_items)
        logger.debug(f"Total price calculated: {total_price} for User ID: {user.id}")
        
        # ===== بررسی موجودی کیف پول مشتری ===== #
        user_balance = self._wallet_service.get_user_balance(user)
        if user_balance < total_price:
            logger.error(
                f"Insufficient funds for User ID: {user.id}. "
                f"Balance: {user_balance}, Required: {total_price}"
            )
            raise InsufficientFundsError(f"موجودی شما {user_balance} است، اما هزینه سفارش {total_price} می‌باشد.")
        
        # ===== شروع فرآیند اتمیک ایجاد سفارش ===== #
        try:
            with transaction.atomic():
                logger.info(f"Transaction started for User ID: {user.id}")

                # ===== ایجاد سفارش اولیه در دیتابیس ===== #
                initial_status = OrderStatus.objects.get(pk=1) 
                order = self._order_repo.create_order(
                    user=user,
                    order_status=initial_status,
                    address=address if address else None,
                    total_price=total_price,
                    order_type="1"
                )
                logger.info(f"Order object created with ID: {order.id}")

                # ===== انتقال آیتم‌های سبد خرید به آیتم‌های سفارش ===== #
                for cart_item in cart_items:
                    order_item = self._order_item_repo.create_order_item(
                        order=order,
                        product=cart_item.product,
                        price=cart_item.price,
                        quantity=cart_item.quantity,
                        items=cart_item.items
                    )
                    
                    # ===== پردازش و انتقال فایل‌های آپلود شده ===== #
                    for upload in cart_item.uploads.all():
                        try:
                            # ===== دریافت مسیر فایل منبع ===== #
                            source_path = upload.file.path
                            file_name = os.path.basename(source_path)

                            # ===== ساخت مسیر جدید و امن برای فایل سفارش ===== #
                            new_relative_path = f'orders/designs/{order.id}/{order_item.id}/{file_name}'
                            new_full_path = os.path.join(settings.MEDIA_ROOT, new_relative_path)
                            os.makedirs(os.path.dirname(new_full_path), exist_ok=True)
                            
                            # ===== کپی کردن فیزیکی فایل ===== #
                            with open(source_path, 'rb') as source_file:
                                file_content = source_file.read()
                            
                            with open(new_full_path, 'wb') as dest_file:
                                dest_file.write(file_content)
                            
                            logger.debug(f"File moved from {source_path} to {new_full_path}")

                            # ===== ثبت رکورد فایل طراحی در دیتابیس ===== #
                            design_file = self._design_file_repo.create_design_file(file_path=new_relative_path)
                            self._order_item_design_file_repo.add_design_file_to_order(
                                order_item=order_item,
                                file_path=design_file,
                                user=user 
                            )
                        except Exception as file_error:
                            logger.error(f"Error moving file for OrderItem {order_item.id}: {file_error}")
                            raise file_error
                    
                # ===== کسر وجه از کیف پول ===== #
                self._wallet_service.debit(user, total_price, transaction_type="6")
                logger.info(f"Wallet debited: {total_price} from User ID: {user.id}")

                # ===== حذف آیتم‌های سبد خرید ===== #
                self._cart_item_repo.delete_items_by_cart(cart)
                logger.info(f"Cart cleared for User ID: {user.id}")
                
            logger.info(f"Order created successfully. Order ID: {order.id}")
            return order
        
        except Exception as e:
            logger.exception(f"Order creation failed for User ID: {user.id} due to unexpected error.")
            raise OrderCreationError("خطا در هنگام ثبت سفارش. لطفاً دوباره تلاش کنید.") from e
        