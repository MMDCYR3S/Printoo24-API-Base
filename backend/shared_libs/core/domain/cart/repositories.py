from typing import Optional, Dict

from core.models import Cart, CartItem, Product, User
from core.utils import BaseRepository

from .exceptions import (
    CartNotFoundException,
    ItemNotFoundException
)

# ======== Cart Repository ======== #
class CartRepository(BaseRepository[Cart]):
    """
    ریپازیتوری برای مدیریت دسترسی به داده‌های مدل Cart.
    """
    def __init__(self):
        super().__init__(model=Cart)

    def get_cart_by_user(self, user: User) -> Optional[Cart]:
        """
        سبد خرید فعال یک کاربر را پیدا می‌کند.
        """
        try:
            return self.model.objects.filter(user=user).first()
        except self.model.DoesNotExist:
            raise CartNotFoundException("سبد خرید برای کاربر پیدا نشد.")
        
    # ===== دریافت یا ساخت سبد خرید ===== #
    def get_or_create_cart(self, user: User) -> Cart:
        """
        اگر یک کاربر یک سبد خرید داشته باشد، آن را باز می‌کند.
        اگر نه، یک سبد خرید جدید را ساخته و باز می‌کند.
        """
        cart, _ = self.model.objects.get_or_create(user=user)
        return cart

# ===== Cart Item Repository ===== #
class CartItemRepository(BaseRepository[CartItem]):
    """
    ریپازیتوری برای مدیریت دسترسی به داده‌های مدل CartItem.
    """
    def __init__(self):
        super().__init__(CartItem)

    # ===== جستجوی آیتم در سبد خرید ===== #
    def find_item_in_cart(self, cart: Cart, product: Product, items: Dict) -> Optional[CartItem]:
        """
        یک آیتم خاص با مشخصات یکسان را در سبد خرید پیدا می‌کند.
        این متد برای جلوگیری از افزودن آیتم تکراری و افزایش تعداد آیتم موجود استفاده می‌شود.
        """
        try:
            return self.model.objects.get(cart=cart, product=product, items=items)
        except self.model.DoesNotExist:
            raise ItemNotFoundException("آیتم در سبد خرید پیدا نشد.")

    # ===== دریافت تمام آیتم‌های یک سبد خرید ===== #
    def get_items_by_cart(self, cart: Cart):
        """
        تمام آیتم‌های یک سبد خرید را برمی‌گرداند.
        """
        return list(self.model.objects.filter(cart=cart).prefetch_related('uploads', 'product'))
    # ===== دریافت جزئیات یک آیتم با چک کردن مالکیت کاربر ===== #
    def get_item_details(self, item_id: int, user: User) -> Optional[CartItem]:
        """
        دریافت جزئیات دقیق یک آیتم خاص با چک کردن مالکیت کاربر.
        """
        try:
            return self.model.objects.select_related(
                'cart',
                'product',
            ).get(
                id=item_id, 
                cart__user=user
            )
        except self.model.DoesNotExist:
            return None
        
    # ===== حذف دسته‌جمعی آیتم‌های یک سبد خرید ===== #
    def delete_all_items_by_cart(self, cart: Cart) -> None:
        """
        تمام آیتم‌های مرتبط با یک سبد خرید را به صورت دسته‌جمعی (bulk) حذف می‌کند.
        این روش بسیار بهینه‌تر از حذف تک به تک است.
        """
        self.model.objects.filter(cart=cart).delete()
        
