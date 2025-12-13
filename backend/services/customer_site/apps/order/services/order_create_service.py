import logging
from typing import List
from django.db import transaction
from rest_framework.exceptions import ValidationError 

from ..exceptions import EmptyCartError, InsufficientFundsError, ItemNotFoundException
from core.models import User, Address, Order, CartItem
from core.domain.commerce.order import CheckoutDomainService
from core.domain.identity.wallet import WalletDomainService
from core.domain.commerce.cart import CartDomainService

logger = logging.getLogger('shop.services.order_creation')

class CreateOrderFromCartService:
    def __init__(self):
        self._checkout_domain = CheckoutDomainService() 
        self._cart_domain = CartDomainService()
        self._wallet_service = WalletDomainService()
        
    @transaction.atomic
    def execute(self, user: User, address: Address, cart_item_id: int, order_type: str = "2") -> Order:
        """
        اجرای فرآیند تسویه حساب برای یک آیتم تکی از سبد خرید (Single Item Checkout).
        """
        logger.info(f"Start checkout for CartItem ID {cart_item_id} by User {user.id}")

        if address is None:
            raise ValidationError("لطفاً آدرس ارسال سفارش را انتخاب کنید.")

        # 1. دریافت آیتم مشخص و چک مالکیت
        # ما باید متد get_item_details را در CartItemRepository یا سرویس دامنه بسازیم
        cart = self._cart_domain._cart_repo.get_cart_by_user(user)
        if not cart:
            raise EmptyCartError("سبد خرید یافت نشد.")

        cart_item = cart.cart_items.filter(id=cart_item_id).select_related('product').prefetch_related('uploads').first()
        if not cart_item:
            raise ItemNotFoundException("آیتم مورد نظر در سبد خرید شما یافت نشد.")
        
        # 2. محاسبه قیمت (فقط قیمت این آیتم)
        item_price = cart_item.price
        
        # 3. چک کردن کیف پول
        user_balance = self._wallet_service.get_user_balance(user)
        if user_balance < item_price:
            logger.warning(f"Insufficient funds: User {user.id}, Need {item_price}, Has {user_balance}")
            raise InsufficientFundsError(f"موجودی کافی نیست. مبلغ سفارش: {item_price:,} تومان")
        
        try:
            # 4. 🚨 اجرای ایجاد سفارش تکی در Domain Service
            order = self._checkout_domain.checkout_single_item(
                user=user, 
                cart_item=cart_item, # ارسال آبجکت آیتم به جای کل سبد خرید
                address=address, 
                order_type=order_type
            )
            
            # 5. کسر از کیف پول
            self._wallet_service.debit(user=user, amount=item_price)
            
            logger.info(f"Order {order.order_code} created successfully for CartItem {cart_item_id}.")
            return order # بازگشت یک Order تکی

        except Exception as e:
            logger.error(f"Order creation failed for CartItem {cart_item_id}: {e}")
            raise e
