from typing import Dict
from django.db import models
from .exceptions import CartNotFoundException, ItemNotFoundException

# ========== BASE QUERYSET ========== #
class BaseQuerySet(models.QuerySet):
    def get_by_id(self, id: int):
        return self.filter(id=id).first()

# ========== CART QUERYSET ========== #
class CartQuerySet(BaseQuerySet):
    """کوئری‌های مربوط به سبد خرید"""
    
    def get_cart_by_user(self, user):
        """
        سبد خرید فعال یک کاربر را پیدا می‌کند.
        """
        try:
            return self.filter(user=user).first()
        except self.model.DoesNotExist:
            return None

    def get_or_create_cart(self, user):
        """
        اگر یک کاربر یک سبد خرید داشته باشد، آن را باز می‌کند.
        اگر نه، یک سبد خرید جدید را ساخته و باز می‌کند.
        """
        cart, _ = self.get_or_create(user=user)
        return cart

# ========== CART MANAGERS ========== #
class CartManager(models.Manager):
    def get_queryset(self):
        return CartQuerySet(self.model, using=self._db)

    def get_cart_by_user(self, user):
        cart = self.get_queryset().get_cart_by_user(user)
        if not cart:
            raise CartNotFoundException("سبد خرید برای کاربر پیدا نشد.")
        return cart

    def get_or_create_cart(self, user):
        return self.get_queryset().get_or_create_cart(user)


# ========== CART ITEM QUERYSET ========== #
class CartItemQuerySet(BaseQuerySet):
    """کوئری‌های مربوط به آیتم‌های سبد"""
    
    def find_item_in_cart(self, cart, product, items: Dict):
        """
        یک آیتم خاص با مشخصات یکسان را در سبد خرید پیدا می‌کند.
        """
        try:
            return self.get(cart=cart, product=product, items=items)
        except self.model.DoesNotExist:
            raise ItemNotFoundException("آیتم در سبد خرید پیدا نشد.")

    def get_items_by_cart(self, cart):
        """
        تمام آیتم‌های یک سبد خرید را برمی‌گرداند.
        """
        return self.filter(cart=cart).prefetch_related('uploads', 'product')

    def get_item_details(self, item_id: int, user):
        """
        دریافت جزئیات دقیق یک آیتم خاص با چک کردن مالکیت کاربر.
        """
        try:
            return self.select_related(
                'cart',
                'product',
            ).get(
                id=item_id, 
                cart__user=user
            )
        except self.model.DoesNotExist:
            return None

# ========== CART ITEM MANAGERS ========== #
class CartItemManager(models.Manager):
    def get_queryset(self):
        return CartItemQuerySet(self.model, using=self._db)

    def find_item_in_cart(self, cart, product, items: Dict):
        return self.get_queryset().find_item_in_cart(cart, product, items)

    def get_items_by_cart(self, cart):
        return self.get_queryset().get_items_by_cart(cart)

    def get_item_details(self, item_id: int, user):
        return self.get_queryset().get_item_details(item_id, user)

    def delete_all_items_by_cart(self, cart):
        """
        تمام آیتم‌های مرتبط با یک سبد خرید را به صورت دسته‌جمعی حذف می‌کند.
        """
        self.filter(cart=cart).delete()
