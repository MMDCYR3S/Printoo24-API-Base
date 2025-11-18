from typing import Optional, Dict, Any

from core.models import Cart, CartItem, Product, User
from .cart_repo import CartRepository, CartItemRepository

# ======= Cart Core Service ======= #
class CartService:
    """
    سرویس برای مدیریت عملیات‌های اصلی سبد خرید.
    """
    def __init__(self, repository = CartRepository()):
        self._repository =repository

    def get_or_create_cart_for_user(self, user: User) -> Cart:
        """
        سبد خرید یک کاربر را برمی‌گرداند. اگر وجود نداشته باشد، یکی جدید می‌سازد.
        ورودی این متد همیشه یک کاربر معتبر است.
        """
        if not user or not user.is_authenticated:
            raise ValueError("کاربر باید وارد سیستم باشد.")
        
        cart = self._repository.get_cart_by_user(user=user)
        
        # ===== در صورت نبود سبد خرید برای کاربر، یکی ساخته می شود ===== #
        if not cart:
            cart = self._repository.create({"user": user})
            
        return cart

# ======== Cart Item Service ======== #
class CartItemService:
    """
    سرویس برای مدیریت عملیات‌های اصلی آیتم‌های سبد خرید.
    """
    def __init__(self, repository: CartItemRepository):
        self._repository = repository

    def add_item(self, cart: Cart, product: Product, quantity: int, price: float, items: Dict[str, Any]) -> CartItem:
        item_data = {
            "cart": cart,
            "product": product,
            "quantity": quantity,
            "price": price,
            "items": items,
        }
        return self._repository.create(item_data)

    def update_item_quantity(self, item: CartItem, quantity: int) -> CartItem:
        return self._repository.update(instance=item, data={"quantity": quantity})

    def remove_item(self, item: CartItem) -> None:
        self._repository.delete(instance=item)

    def find_item(self, cart: Cart, product: Product, items: Dict) -> Optional[CartItem]:
        return self._repository.find_item_in_cart(cart=cart, product=product, items=items)
    