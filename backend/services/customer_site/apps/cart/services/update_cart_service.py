import logging
from typing import Dict, Any
from apps.cart.models import CartItem
from apps.cart.domain_services import CartService

logger = logging.getLogger('cart.services.update')

# ========== CART ITEM UPDATE SERVICE ========== #
class CartItemUpdateService:
    """
    سرویس اپلیکیشن برای آپدیت آیتم سبد خرید.
    پشتیبانی از تغییر تعداد و تغییر آپشن‌ها (Full Update).
    """
    def __init__(self, user):
        self.user = user
        self.domain_service = CartService()
        
    def update(self, cart_item_id: int, raw_data: Dict[str, Any]) -> CartItem:
        """
        اجرای عملیات بروزرسانی آیتم سبد خرید.
        """
        logger.info(f"Update Item {cart_item_id} for User {self.user.id}")
        
        try:
            # ===== دریافت تیراژ یا تعداد جدید ===== #
            quantity_input = int(raw_data.pop('quantity', 1))
            
            # ===== اجرای عملیات بروزرسانی ===== #
            updated_item = self.domain_service.update_cart_item(
                user=self.user,
                item_id=cart_item_id,
                quantity_input=quantity_input,
                selections=raw_data
            )
            # ===== بازگشت اطلاعات آیتم ===== #
            logger.info(f"Item {cart_item_id} updated/merged.")
            return updated_item

        except Exception as e:
            logger.error(f"Update cart item failed: {str(e)}")
            raise e
