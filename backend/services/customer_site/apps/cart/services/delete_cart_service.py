import logging

from django.db.models import Q
from rest_framework.exceptions import NotFound

from core.models import User
from apps.cart.models import CartItem, Cart
from ..exceptions import ItemNotFoundException

# ===== تعریف لاگر اختصاصی برای سرویس‌های حذف ===== #
logger = logging.getLogger('cart.services.delete')

# ====== Cart Item Delete Service ====== #
class CartItemDeleteService:
    """
    سرویس حذف تکی آیتم (پشتیبانی از Guest و Auth).
    """
    
    def __init__(self, user: User = None, session_key: str = None):
        self.user = user if (user and user.is_authenticated) else None
        self.session_key = session_key

        if not self.user and not self.session_key:
            raise NotFound("نشست کاربری نامعتبر است.")
        
    def delete(self, item_id: int) -> None:
        """
        حذف آیتم با بررسی مالکیت.
        """
        # ===== لاگ برای چک کردن ===== #
        user_log = self.user.id if self.user else f"Guest-{self.session_key}"
        logger.info(f"Request delete Item {item_id} for {user_log}")
        
        # ===== دریافت آیتم کاربر ===== #
        query = Q(id=item_id)
        if self.user:
            query &= Q(cart__user=self.user)
        else:
            query &= Q(cart__session_key=self.session_key, cart__user__isnull=True)
        
        try:
            # ===== دریافت آیتم ===== #
            item = CartItem.objects.get(query)
            item.delete()
            logger.info(f"Item {item_id} deleted successfully.")
        
        # ===== اگر آیتم یافت نشد ===== #
        except CartItem.DoesNotExist:
            logger.warning(f"Item {item_id} not found or access denied.")
            raise NotFound("آیتم یافت نشد یا متعلق به شما نیست.")
        
class CartClearService:
    """
    سرویس پاکسازی کل سبد خرید (پشتیبانی از Guest و Auth).
    """
    
    def __init__(self, user: User = None, session_key: str = None):
        # ===== تشخیص کاربر ===== #
        self.user = user if (user and user.is_authenticated) else None
        self.session_key = session_key
        
        # ===== اگر کاربری وجود نداشت ===== #    
        if not self.user and not self.session_key:
             raise NotFound("نشست کاربری نامعتبر است.")
         
    def clear(self) -> None:
        """
        پاک کردن تمام آیتم‌های سبد خرید.
        """
        user_log = self.user.id if self.user else f"Guest-{self.session_key}"
        logger.info(f"Request clear cart for {user_log}")
        
        try:
            # ===== دریافت سبد خرید ===== #
            if self.user:
                cart = Cart.objects.filter(user=self.user).first()
            else:
                cart = Cart.objects.filter(session_key=self.session_key, user__isnull=True).first()

            if cart:
                # ===== پاک کردن تمام آیتم‌های سبد خرید ===== #
                count, _ = cart.cart_items.all().delete()
                logger.info(f"Cart {cart.id} cleared. Removed {count} items.")
            else:
                logger.info("Cart not found (already empty).")
                
        except Exception as e:
            logger.error(f"Error clearing cart: {str(e)}")
            raise e
        