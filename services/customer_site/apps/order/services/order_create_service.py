import os
import logging
from decimal import Decimal
from django.db import transaction
from django.conf import settings

from ..exceptions import (
    EmptyCartError,
    InsufficientFundsError
)
from core.models import User, Address, Order
from core.domain.order.services import OrderDomainService
from core.domain.wallet.services import WalletDomainService
from core.domain.cart.services import CartDomainService

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
        self._order_domain = OrderDomainService()
        self._cart_domain = CartDomainService()
        self._wallet_service = WalletDomainService()
        
    @transaction.atomic
    def execute(self, user: User, address: Address | None, order_type: str = "1") -> Order:
        """
        تبدیل سبد خرید کاربر به سفارش نهایی.
        در این متد، با استفاده از یک سرویس دامنه، قوانین و محدودیت ها
        بررسی می شود و پس از آن، عملیات ثبت سفارش انجام می‌پذیرد.
        """
        logger.info(f"Starting order creation for User ID: {user.id}")
        logger.info(f"Starting order creation process for User ID: {user.id}")

        # ===== دریافت یا ایجاد سبد خرید کاربر ===== #
        cart = self._cart_domain.get_or_create_cart_for_user(user)
        if not cart or not cart.cart_items.exists():
            raise EmptyCartError("سبد خرید خالی است.")
        
        # ===== محاسبه قیمت کل سبد خرید ===== #
        total_price = sum(item.price for item in cart.cart_items.all())
        
        # ===== دریافت موجودی کیف پول کاربر ===== #
        user_balance = self._wallet_service.get_user_balance(user)
        if user_balance < total_price:
            logger.error(f"Insufficient funds: Balance {user_balance} < Total {total_price}")
            raise InsufficientFundsError(f"موجودی کافی نیست. هزینه سفارش: {total_price}")
        
        try:
            # ===== ایجاد سفارش از طریق سرویس دامنه ===== #
            order = self._order_domain.checkout_cart(
                user=user, 
                address=address, 
                order_type=order_type
            )
            
            # ===== کسر مبلغ از کیف پول کاربر ===== #
            self._wallet_service.debit(user=user, amount=total_price)
            
            logger.info(f"Order created successfully: {order.id}")
            return order
        except Exception as e:
            logger.exception(f"Order creation failed for User {user.id}")
            raise e
             