import logging

from rest_framework.exceptions import NotFound

from core.models import User
from core.domain.cart.services import CartDomainService
from core.domain.cart.exceptions import ItemNotFoundException

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
        self._domain_service = CartDomainService()
        
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
            self._domain_service.remove_item(self.user, item_id)
            logger.info("Item deleted successfully")
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
        # ===== تزریق وابستگی‌ها ===== #
        self._domain_service = CartDomainService()
        
    def clear(self) -> None:
        """
        حذف تمام آیتم‌های سبد خرید کاربر.
        """
        logger.info(f"Request to clear entire cart for User ID: {self.user.id}")
        
    def clear(self) -> None:
        try:
            logger.info(f"Clearing cart for user {self.user.id}")
            self._domain_service.clear_cart(self.user)
        except Exception as e:
            logger.error(f"Error clearing cart for user {self.user.id}: {str(e)}")
            raise e