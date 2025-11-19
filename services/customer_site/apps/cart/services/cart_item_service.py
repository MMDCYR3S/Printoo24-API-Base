from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
from django.core.exceptions import ObjectDoesNotExist

from core.models import CartItem, User, Cart
from core.common.cart import (
    CartRepository,
    CartItemRepository,
    CartService,
    CartItemService
)

# ===== Cart List Service ===== #
class CartListService:
    """
    سرویس نمایش لیست آیتم‌های سبد خرید کاربر.
    """
    def __init__(self, 
                 cart_repo: CartRepository = None, 
                 item_repo: CartItemRepository = None,
                 cart_service: CartService = None,
                 cart_item_service: CartItemService = None,
        ):
        # ===== تزریق وابستگی ها ===== #
        self._cart_repo = cart_repo or CartRepository()
        self._item_repo = item_repo or CartItemRepository()
        self._cart_service = cart_service or CartService(self._cart_repo)
        self._cart_item_service = cart_item_service or CartItemService(self._item_repo)
        
    def get_user_cart_items(self, user: User) -> dict:
        """
        سبد خرید و آیتم‌های آن را برمی‌گرداند.
        """
        # ===== دریافت  یا ایجاد سبد خرید ===== #
        cart = self._cart_service.get_or_create_cart_for_user(user)
        # ===== دریافت آیتم‌های سسبد خرید ===== #
        items = self._cart_item_service.get_user_cart_items(cart)
        
        return {
            "cart": cart,
            "items": items
        }

# ======= Cart Item Detail Service ======= #
class CartItemDetailService:
    """
    سرویس نمایش جزئیات یک آیتم خاص.
    """
    def __init__(self):
        self._item_repo = CartItemRepository(),
        self._cart_item_service = CartItemService(repository=CartItemRepository())
        
    def get_item_detail(self, item_id: int, user: User) -> CartItem:
        """
        جزئیات آیتم را برمی‌گرداند یا ارور می‌دهد.
        """
        item = self._cart_item_service.get_item_detail(item_id=item_id, user=user)

        if not item:
            raise ObjectDoesNotExist("آیتم مورد نظر یافت نشد یا متعلق به شما نیست.")
            
        return item
