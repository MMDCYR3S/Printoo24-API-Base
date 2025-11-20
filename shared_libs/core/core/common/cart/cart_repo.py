from typing import Optional, Dict

from django.db.models import Q
from ...models import Cart, CartItem, Product, User
from ...common.repositories import IRepository

# ======== Cart Repository ======== #
class CartRepository(IRepository[Cart]):
    """
    ریپازیتوری برای مدیریت دسترسی به داده‌های مدل Cart.
    """
    def __init__(self):
        super().__init__(Cart)

    def get_cart_by_user(self, user: User) -> Optional[Cart]:
        """
        سبد خرید فعال یک کاربر را پیدا می‌کند.
        با توجه به اینکه رابطه یک به یک است، از get() استفاده می‌کنیم.
        """
        try:
            return self.model.objects.get(user=user)
        except Cart.DoesNotExist:
            return None

# ===== Cart Item Repository ===== #
class CartItemRepository(IRepository[CartItem]):
    """
    ریپازیتوری برای مدیریت دسترسی به داده‌های مدل CartItem.
    """
    def __init__(self):
        super().__init__(CartItem)

    def find_item_in_cart(self, cart: Cart, product: Product, items: Dict) -> Optional[CartItem]:
        """
        یک آیتم خاص با مشخصات یکسان را در سبد خرید پیدا می‌کند.
        این متد برای جلوگیری از افزودن آیتم تکراری و افزایش تعداد آیتم موجود استفاده می‌شود.
        """
        try:
            return self.model.objects.get(cart=cart, product=product, items=items)
        except self.model.DoesNotExist:
            return None

    def get_items_for_cart(self, cart: Cart):
        """
        تمام آیتم‌های یک سبد خرید را برمی‌گرداند.
        """
        return self.filter(cart=cart)

    def get_items_for_cart_with_relations(self, cart: Cart):
        """
        دریافت تمام آیتم‌های سبد خرید با بارگذاری روابط (برای لیست).
        """
        return self.filter(cart=cart)

    def get_item_detail_with_relations(self, item_id: int, user: User) -> Optional[CartItem]:
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
        
    def delete_items_by_cart(self, cart: Cart) -> None:
        """
        تمام آیتم‌های مرتبط با یک سبد خرید را به صورت دسته‌جمعی (bulk) حذف می‌کند.
        این روش بسیار بهینه‌تر از حذف تک به تک است.
        """
        self.model.objects.filter(cart=cart).delete()
        
