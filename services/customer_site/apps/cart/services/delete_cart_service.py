from rest_framework.exceptions import NotFound

from core.models import User, CartItem
from core.common.cart import CartService, CartItemService, CartItemRepository, CartRepository

# ====== Cart Item Delete Service ====== #
class CartItemDeleteService:
    """
    سرویس برای حذف یک آیتم مشخص از سبد خرید کاربر.
    """
    def __init__(self, user: User):
        self.user = user
        self._cart_item_service = CartItemService(repository=CartItemRepository())
        
    def delete(self, item_id: int) -> None:
        """
        یک آیتم را بر اساس شناسه آن پیدا کرده و حذف می‌کند.
        این متد مالکیت آیتم را نیز بررسی می‌کند.
        """

        try:
            # ===== دریافت جزئیات آیتم با بررسی مالکیت کاربر ===== #
            item_to_delete = self._cart_item_service.get_item_detail(item_id=item_id, user=self.user)
            # ===== حذف آیتم ===== #
            self._cart_item_service.delete_item(item_to_delete)
            
        except ValueError:
            raise NotFound("آیتم مورد نظر در سبد خرید شما یافت نشد.")
        
# ====== Cart Clear Service ====== #
class CartClearService:
    """
    سرویس برای حذف تمام آیتم‌های سبد خرید کاربر.
    """
    
    def __init__(self, user: User):
        self.user = user
        self.cart_service = CartService(repository=CartRepository())
        self._cart_item_service = CartItemService(repository=CartItemRepository())
        
    def clear(self) -> None:
        """
        سبد خرید کاربر را پیدا کرده و تمام آیتم‌های آن را حذف می‌کند.
        """
        # ===== دریافت سبد خرید کاربر ===== #
        cart = self.cart_service._repository.get_cart_by_user(user=self.user)
        if cart:
            self._cart_item_service.delete_all_items_for_cart(cart=cart)