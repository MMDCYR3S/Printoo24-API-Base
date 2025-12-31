import logging
from typing import Dict, Any

from django.db import transaction
from django.core.exceptions import ValidationError

from core.models import User, Product
from apps.cart.models import Cart, CartItem
from apps.cart.utils import CartProcessor

logger = logging.getLogger('cart.services.add_to_cart')

# ========== ADD TO CART SERVICE ========== #
class AddToCartService:
    """
    سرویس افزودن آیتم به سبد خرید.
    مسئولیت‌ها:
    1. فراخوانی Processor برای محاسبات
    2. مدیریت سبد خرید (ایجاد/دریافت)
    3. مدیریت تکراری بودن آیتم (Merge)
    4. ذخیره نهایی
    """
    def __init__(self, user: User = None, session_key: str = None):
        self.user = user if (user and user.is_authenticated) else None
        self.session_key = session_key
        
        # گارد: حداقل یکی باید باشد
        if not self.user and not self.session_key:
             raise ValidationError("شناسه کاربر یا شناسه مهمان الزامی است.")
        
    @transaction.atomic
    def execute(self, product_id: int, selections: Dict[str, Any]) -> CartItem:
        logger.info(f"Start adding product {product_id} for user {self.user.id}")

        try:
            # ===== دریافت محصول ===== #
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            raise ValidationError("محصول یافت نشد یا غیرفعال است.")
        
        # ===== دریافت تیراژ یا تعداد ===== #
        quantity_input = int(selections.pop('quantity', 1))
        
        # ===== پردازش منطقی سبد خرید ===== #
        processor = CartProcessor(product, selections, quantity_input).process()

        # ===== دریافت یا ایجاد سبد خرید ===== #
        cart = self._get_or_create_cart()

        # ===== چک کردن تکراری بودن آیتم ===== #
        existing_item = CartItem.objects.find_duplicate_item(
            cart=cart, 
            product=product, 
            items_data=processor.result_item_data
        )
        
        # ===== اگر آیتم وجود داشت، فقط تیراژ و قیمت رو افزایش بده ===== #
        if existing_item:
            logger.info(f"Merging with existing item {existing_item.id}")
            existing_item.quantity += processor.result_quantity
            existing_item.price = processor.result_price

            existing_item.save()
            return existing_item
        else:
            # ===== ایجاد آیتم جدید ===== #
            logger.info("Creating new cart item")
            new_item = CartItem.objects.create(
                cart=cart,
                product=product,
                name=processor.result_name,
                quantity=processor.result_quantity,
                price=processor.result_price,
                items=processor.result_item_data,
                description=processor.result_description
            )
            return new_item

    def _get_or_create_cart(self) -> Cart:
        """ یافتن سبد خرید بر اساس اولویت: کاربر لاگین > سشن مهمان """
        if self.user:
            cart, _ = Cart.objects.get_or_create(user=self.user)
            return cart
        else:
            cart, _ = Cart.objects.get_or_create(session_key=self.session_key, user=None)
            return cart
