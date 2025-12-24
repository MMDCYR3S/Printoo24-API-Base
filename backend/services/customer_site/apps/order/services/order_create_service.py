import logging
from typing import List
from django.db import transaction
from rest_framework.exceptions import ValidationError 

from ..exceptions import EmptyCartError, InsufficientFundsError, ItemNotFoundException
from core.models import User, Address, Order, CartItem
from core.order.services import CheckoutService
from core.users.services import WalletService
from core.cart.services import CartService

logger = logging.getLogger('shop.services.order_creation')

class CreateOrderFromCartService:
    def __init__(self):
        self._checkout_domain = CheckoutService() 
        self._cart_domain = CartService()
        self._wallet_service = WalletService()
        
    @transaction.atomic
    def execute(self, user: User, address: Address, cart_item_id: int, order_type: str = "1") -> Order:
        """
        اجرای فرآیند تسویه حساب برای یک آیتم تکی (Single Item Checkout).
        """
        logger.info(f"Start checkout for CartItem ID {cart_item_id} by User {user.id}")
        # ===== چک کردن آدرس مشتری و در صورت نبود، خطا دادن ===== #
        if not address:
            raise ValidationError("لطفاً آدرس ارسال سفارش را انتخاب کنید.")

        # ===== دریافت سبد خرید ===== # 
        cart = self._cart_domain.get_or_create_cart_for_user(user)
        if not cart:
            raise EmptyCartError("سبد خرید یافت نشد.")
        # ===== تلاش برای دریافت آیتم ===== #
        try:
            cart_item = self._cart_domain.get_cart_item_for_user(user, cart_item_id)
        except Exception:
            raise ItemNotFoundException("آیتم مورد نظر در سبد خرید یافت نشد.")
        
        # ===== محاسبه قیمت ===== #
        item_price = cart_item.price
        # ===== دریافت کیف پول ===== #
        user_balance = self._wallet_service.get_user_balance(user)
        # ===== چک کردن کیف پول ===== #
        if user_balance < item_price:
            logger.warning(f"Insufficient funds: User {user.id}, Need {item_price}, Has {user_balance}")
            raise InsufficientFundsError(f"موجودی کافی نیست. مبلغ سفارش: {item_price:,} تومان")
        
        try:
            # ===== کسر مبلغ از کیف پول ===== #
            self._wallet_service.debit(user=user, amount=item_price)
            
            # ===== تسویه حساب ===== #
            order = self._checkout_domain.checkout_single_item(
                user=user, 
                cart_item=cart_item,
                address=address, 
                order_type=order_type
            )
            
            logger.info(f"Order {order.order_code} created successfully for CartItem {cart_item_id}.")
            return order

        except Exception as e:
            logger.error(f"Order creation failed for CartItem {cart_item_id}: {e}")
            raise e

    @transaction.atomic
    def execute_bulk(self, user: User, address: Address, order_type: str = "1") -> List[Order]:
        """
        اجرای فرآیند تسویه حساب برای کل سبد خرید (Bulk Checkout).
        """
        logger.info(f"Start BULK checkout for User {user.id}")
        # ===== در صورت نبود آدرس، خطا ===== #
        if address is None:
            raise ValidationError("لطفاً آدرس ارسال سفارش را انتخاب کنید.")
        
        # ===== دریافت سبد خرید و آیتم ها ===== #
        cart = self._cart_domain.get_or_create_cart_for_user(user)
        if not cart or not cart.cart_items.exists():
            raise EmptyCartError("سبد خرید شما خالی است.")
        # ===== دریافت آیتم ها ===== #
        cart_items = list(cart.cart_items.select_related('product').prefetch_related('uploads').all())
        # ===== اگر آیتمی نبود ===== #
        if not cart_items:
            raise EmptyCartError("سبد خرید شما خالی است.")
        
        # ===== محاسبه قیمت ===== #
        total_price = sum(item.price for item in cart_items)
        
        # ===== چک کردن کیف پول ===== #
        user_balance = self._wallet_service.get_user_balance(user)
        if user_balance < total_price:
            logger.warning(f"Insufficient funds for bulk: User {user.id}, Need {total_price}, Has {user_balance}")
            raise InsufficientFundsError(f"موجودی کافی نیست. مبلغ کل سفارشات: {total_price:,} تومان")
        
        created_orders = []
        
        try:
            # ===== کسر از کیف پول ===== #
            self._wallet_service.debit(user=user, amount=total_price)
            
            # ===== حلقه برای ساخت سفارش های جداگانه ===== #
            for cart_item in cart_items:
                order = self._checkout_domain.checkout_single_item(
                    user=user, 
                    cart_item=cart_item,
                    address=address, 
                    order_type=order_type
                )
                created_orders.append(order)
            
            logger.info(f"Bulk checkout completed. {len(created_orders)} orders created for User {user.id}.")
            return created_orders

        except Exception as e:
            logger.error(f"Bulk checkout failed for User {user.id}: {e}")
            raise e
