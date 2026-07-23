import logging
from typing import Dict, Any

from django.db import transaction
from django.core.exceptions import ValidationError

from core.models import User, Product
from apps.cart.models import Cart, CartItem
from apps.cart.utils.cart_processor import CartProcessor
from core.infrastructure.messages import msg_provider

logger = logging.getLogger('cart.services.add_to_cart')

class AddToCartService:
    """
    سرویس افزودن آیتم به سبد خرید.
    """
    def __init__(self, user: User = None, session_key: str = None):
        self.user = user if (user and user.is_authenticated) else None
        self.session_key = session_key
        
        if not self.user and not self.session_key:
             raise ValidationError(msg_provider.get("cart.E4019", default="نشست کاربری یا سشن یافت نشد."))
        
    @transaction.atomic
    def execute(self, product_id: int, selections: Dict[str, Any]) -> CartItem:
        logger.info(f"Start adding product {product_id} to cart")

        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            raise ValidationError(msg_provider.get("cart.E4020", default="محصول مورد نظر یافت نشد یا غیرفعال است."))
        
        # ===== پردازش منطقی سبد خرید و محاسبه قیمت ===== #
        processor = CartProcessor(product, selections).process()

        # ===== دریافت یا ایجاد سبد خرید ===== #
        cart = self._get_or_create_cart()

        # ===== چک کردن تکراری بودن آیتم (بر اساس JSON کانفیگ) ===== #
        existing_item = CartItem.objects.find_duplicate_item(
            cart=cart, 
            product=product, 
            items_data=processor.result_item_data
        )
        
        if existing_item:
            logger.info(f"Merging with existing item {existing_item.id}")
            existing_item.quantity += 1
            existing_item.price = processor.result_price * existing_item.quantity 
            existing_item.save()
            return existing_item
            
        else:
            logger.info("Creating new cart item")
            new_item = CartItem.objects.create(
                cart=cart,
                product=product,
                name=processor.result_name,
                quantity=1,
                price=processor.result_price,
                items=processor.result_item_data, 
                description=processor.result_description
            )
            return new_item

    def _get_or_create_cart(self) -> Cart:
        if self.user:
            cart, _ = Cart.objects.get_or_create(user=self.user)
            return cart
        else:
            cart, _ = Cart.objects.get_or_create(session_key=self.session_key, user=None)
            return cart
