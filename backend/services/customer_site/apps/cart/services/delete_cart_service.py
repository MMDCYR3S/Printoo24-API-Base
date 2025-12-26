import logging

from rest_framework.exceptions import NotFound

from core.models import User
from apps.cart.models import CartItem, Cart
from ..exceptions import ItemNotFoundException

# ===== تعریف لاگر اختصاصی برای سرویس‌های حذف ===== #
logger = logging.getLogger('cart.services.delete')

# ====== Cart Item Delete Service ====== #
class CartItemDeleteService:
    """
    سرویس مدیریت حذف تکی آیتم‌های سبد خرید.
    
    این سرویس وظیفه دارد درخواست حذف یک آیتم را دریافت کرده،
    مالکیت کاربر بر آن آیتم را بررسی کند و سپس اقدام به حذف نماید.
    """
    
    def __init__(self, user: User):
        self.user = user
        
    def delete(self, item_id: int) -> None:
        """
        حذف یک آیتم مشخص از سبد خرید.

        Args:
            item_id (int): شناسه آیتم سبد خرید.

        Raises:
            NotFound: اگر آیتم یافت نشود یا متعلق به کاربر نباشد.
        """
        logger.info(f"Request to delete CartItem ID: {item_id} for User ID: {self.user.id}")

        try:
            # ===== دریافت جزئیات آیتم با بررسی مالکیت کاربر ===== #
            item = CartItem.objects.get_item_details(item_id, self.user)
            item.delete()
            logger.info("Item deleted")
        except ItemNotFoundException:
            logger.warning(f"Item {item_id} not found")
            raise NotFound("آیتم یافت نشد.")
        
# ====== Cart Clear Service ====== #
class CartClearService:
    """
    سرویس مدیریت پاکسازی کامل سبد خرید.
    
    این سرویس تمام آیتم‌های موجود در سبد خرید کاربر را به یکباره حذف می‌کند.
    """
    
    def __init__(self, user: User):
        self.user = user

    def clear(self) -> None:
        """
        حذف تمام آیتم‌های سبد خرید کاربر.
        """
        logger.info(f"Request to clear entire cart for User ID: {self.user.id}")
        
    def clear(self) -> None:
        try:
            cart = Cart.objects.get_cart_by_user(self.user)
            CartItem.objects.delete_all_items_by_cart(cart)
        except Exception as e:
            logger.error(f"Error clearing cart for user {self.user.id}: {str(e)}")
            raise e