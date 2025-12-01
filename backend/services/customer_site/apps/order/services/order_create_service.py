import logging
from django.db import transaction

from ..exceptions import EmptyCartError, InsufficientFundsError
from core.models import User, Address, Order
from core.domain.order.services import OrderDomainService
from core.domain.wallet.services import WalletDomainService
from core.domain.cart.services import CartDomainService

logger = logging.getLogger('shop.services.order_creation')

class CreateOrderFromCartService:
    """
    ارکستراتور ثبت سفارش:
    1. چک کیف پول
    2. فراخوانی دامین اردر (ساخت سفارش + جابجایی فایل)
    3. کسر از کیف پول
    """
    
    def __init__(self):
        self._order_domain = OrderDomainService()
        self._cart_domain = CartDomainService()
        self._wallet_service = WalletDomainService()
        
    @transaction.atomic
    def execute(self, user: User, address: Address | None, order_type: str = "1") -> Order:
        logger.info(f"Process start: Create Order for User {user.id}")

        # ===== بررسی خالی بودن سبد خرید ===== #
        cart = self._cart_domain.get_or_create_cart_for_user(user)
        if not cart or not cart.cart_items.exists():
            raise EmptyCartError("سبد خرید شما خالی است.")
        
        # ===== محاسبه قیمت نهایی هر آیتم ===== #
        total_price = sum(item.price for item in cart.cart_items.all())
        
        # ===== دریافت حساب کاربر و کیف پول آن و اعتبارسنجی ===== #
        user_balance = self._wallet_service.get_user_balance(user)
        if user_balance < total_price:
            logger.warning(f"Insufficient funds: User {user.id}, Balance {user_balance}, Needed {total_price}")
            raise InsufficientFundsError(f"موجودی کیف پول کافی نیست. مبلغ قابل پرداخت: {total_price}")
        
        try:
            # ===== ساخت سفارش ===== #
            order = self._order_domain.checkout_cart(
                user=user, 
                address=address, 
                order_type=order_type
            )
            
            # ===== برداشت از کیف پول کاربر ===== #
            self._wallet_service.debit(user=user, amount=total_price)
            
            logger.info(f"Order {order.id} created successfully.")
            return order

        except Exception as e:
            logger.error(f"Order creation failed: {e}")
            raise e
