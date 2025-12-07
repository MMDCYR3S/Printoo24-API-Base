import logging
from django.db import transaction
from rest_framework.exceptions import ValidationError # استفاده از ValidationError برای خطای کلاینت

from ..exceptions import EmptyCartError, InsufficientFundsError
from core.models import User, Address, Order
from core.domain.commerce.order import OrderDomainService
from core.domain.identity.wallet import WalletDomainService
from core.domain.commerce.cart import CartDomainService

logger = logging.getLogger('shop.services.order_creation')

class CreateOrderFromCartService:
    def __init__(self):
        self._order_domain = OrderDomainService()
        self._cart_domain = CartDomainService()
        self._wallet_service = WalletDomainService()
        
    @transaction.atomic
    def execute(self, user: User, address: Address | None, order_type: str = "1") -> Order:
        logger.info(f"Start checkout for User {user.id}")

        # 0. اعتبارسنجی آدرس (اصلاحیه مهم)
        if address is None:
            raise ValidationError("لطفاً آدرس ارسال سفارش را انتخاب کنید.")

        # 1. چک کردن سبد خرید
        cart = self._cart_domain._cart_repo.get_cart_by_user(user)
        if not cart or not cart.cart_items.exists():
            raise EmptyCartError("سبد خرید شما خالی است.")
        
        # 2. محاسبه قیمت
        total_price = sum(item.price for item in cart.cart_items.all())
        
        # 3. چک کردن کیف پول
        user_balance = self._wallet_service.get_user_balance(user)
        if user_balance < total_price:
            logger.warning(f"Insufficient funds: User {user.id}, Need {total_price}, Has {user_balance}")
            raise InsufficientFundsError(f"موجودی کافی نیست. مبلغ سفارش: {total_price:,} تومان")
        
        try:
            # 4. ایجاد سفارش
            order = self._order_domain.checkout_cart(
                user=user, 
                address=address, 
                order_type=order_type
            )
            
            # 5. کسر از کیف پول
            self._wallet_service.debit(user=user, amount=total_price)
            
            logger.info(f"Order {order.id} created successfully.")
            return order

        except Exception as e:
            logger.error(f"Order creation failed: {e}")
            raise e
