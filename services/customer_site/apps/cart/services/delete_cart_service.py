import logging
from rest_framework.exceptions import NotFound

from core.models import User
from core.common.cart import (
    CartService,
    CartItemService,
    CartItemRepository,
    CartRepository
)

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
        # ===== تزریق وابستگی‌ها ===== #
        self._cart_item_service = CartItemService(repository=CartItemRepository())
        
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
            item_to_delete = self._cart_item_service.get_item_detail(item_id=item_id, user=self.user)
            
            if not item_to_delete:
                 # نکته: معمولا get_item_detail اگر پیدا نکند None برمیگرداند، اما اگر Raise کرد در except مدیریت میشود
                 raise ValueError("Item not found")

            # ===== حذف آیتم ===== #
            self._cart_item_service.delete_item(item_to_delete)
            logger.info(f"CartItem ID: {item_id} deleted successfully.")
            
        except ValueError:
            logger.warning(f"Delete failed. CartItem {item_id} not found for User ID: {self.user.id}")
            raise NotFound("آیتم مورد نظر در سبد خرید شما یافت نشد.")
        except Exception as e:
            logger.exception(f"Unexpected error deleting CartItem {item_id}")
            raise e
        
# ====== Cart Clear Service ====== #
class CartClearService:
    """
    سرویس مدیریت پاکسازی کامل سبد خرید.
    
    این سرویس تمام آیتم‌های موجود در سبد خرید کاربر را به یکباره حذف می‌کند.
    """
    
    def __init__(self, user: User):
        self.user = user
        # ===== تزریق وابستگی‌ها ===== #
        self.cart_service = CartService(repository=CartRepository())
        self._cart_item_service = CartItemService(repository=CartItemRepository())
        
    def clear(self) -> None:
        """
        حذف تمام آیتم‌های سبد خرید کاربر.
        """
        logger.info(f"Request to clear entire cart for User ID: {self.user.id}")
        
        try:
            # ===== دریافت سبد خرید کاربر ===== #
            cart = self.cart_service._repository.get_cart_by_user(user=self.user)
            
            if cart:
                count = cart.items.count() # فرض بر وجود ریلیشن items
                # ===== حذف تمام آیتم‌ها ===== #
                self._cart_item_service.delete_all_items_for_cart(cart=cart)
                logger.info(f"Cart cleared for User ID: {self.user.id}. {count} items removed.")
            else:
                logger.warning(f"No active cart found to clear for User ID: {self.user.id}")
                
        except Exception as e:
            logger.exception(f"Unexpected error clearing cart for User ID: {self.user.id}")
            raise e
