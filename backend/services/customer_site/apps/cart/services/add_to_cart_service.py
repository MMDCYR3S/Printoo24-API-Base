import logging
from typing import Dict, Any
from django.db import transaction
from core.models import User, CartItem
from core.cart.services import CartService

logger = logging.getLogger('cart.services.add_to_cart')

# ========== ADD TO CART SERVICE ========== #
class AddToCartService:
    """
    سرویس اپلیکیشن برای افزودن محصول به سبد خرید.
    وظیفه: دریافت دیتای خام از کنترلر و پاس دادن به دامین.
    """
    def __init__(self, user: User):
        self.user = user
        self.domain_service = CartService()
        
    @transaction.atomic
    def execute(self, product_id: int, selections: Dict[str, Any]) -> CartItem:
        logger.info(f"Adding product ID {product_id} to cart for user {self.user.id}")
        
        try:
            # ===== دریافت تیراژ و تعداد مورد نظر از مشتری ===== #
            quantity_input = int(selections.pop('quantity', 1))
            
            # ===== افزودن محصول به سبد خرید ===== #
            cart_item = self.domain_service.add_item_to_cart(
                user=self.user,
                product_id=product_id,
                quantity_input=quantity_input,
                selections=selections
            )
            # ===== بازگشت اطلاعات ===== #
            logger.info(f"CartItem created/updated successfully: {cart_item.id}")
            return cart_item

        except Exception as e:
            logger.error(f"Add to cart failed: {str(e)}")
            raise e
