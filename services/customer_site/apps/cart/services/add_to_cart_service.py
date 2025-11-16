from typing import Dict, Any, Optional

from django.db import transaction
from django.core.files.uploadedfile import UploadedFile
from rest_framework.exceptions import ValidationError

from shared_libs.core.core.models import User, CartItem
from shared_libs.core.core.common.cart import CartService, CartItemService
from apps.shop.services import ProductPriceCalculator
from .cart_file_service import CartFileHandlerService
from .cart_validator_service import CartDataValidator

# ====== Add To Cart Service ====== #
class AddToCartService:
    """
    سرویس اصلی و ارکستراتور برای افزودن یک محصول به سبد خرید.
    این سرویس از سرویس‌های کوچک‌تر برای انجام وظایف خود استفاده می‌کند.
    """
    
    def __init__(self, user: User):
        self.user = user
        # ===== تزریق وابستگی های لازم ===== #
        self.cart_service = CartService()
        self.cart_item_service = CartItemService()
        self.validator = CartDataValidator()
        self.file_handler = CartFileHandlerService()
        
    @transaction.atomic
    def execute(
        self,
        product_slug: str,
        quantity: int,
        selections: Dict[str, Any],
        files: Dict[str, UploadedFile]
    ) -> CartItem:
        """
        نقطه ورود اصلی برای اجرای کامل فرآیند افزودن به سبد خرید.
        این متد به صورت اتمیک اجرا می‌شود.
        """
        
        # ====== اعتبارسنجی داده های ورودی کاربر و محصول ====== #
        product = self.validator.validate(product_slug=product_slug, selections=selections)
        
        # ===== دریافت اطلاعات از سمت انتخاب های کاربر ===== #
        product_id = selections.get("product_id")
        quantity_id = selections.get("quantity_id")
        material_id = selections.get("material_id")
        size_id = selections.get("size_id")
        option_ids = selections.get("option_ids")
        custom_dimensions = selections.get("custom_dimensions")
        # ===== محاسبه قیمت نهایی ===== #
        price_calculator = ProductPriceCalculator(product=product_id, quantity=quantity_id, material=material_id, options=option_ids, size=size_id, custom_dimensions=custom_dimensions)
        price = price_calculator.calculate()
        
        # ===== دریافت سبد خرید یا ایجاد آن برای کاربر ===== #
        cart = self.cart_service.get_or_create_cart_for_user(user=self.user)
        
        # ===== ایجاد آیتم های داخل آیتم سبد خرید ===== #
        item_details = {
            "selections": selections,
            "product_name_snapshot": product.name
        }
        
        # ===== ایجاد آیتم سبد خرید ===== #
        cart_item = self.cart_item_service.add_item(
            cart=cart,
            product=product,
            quantity=quantity,
            price=price,
            details=item_details
        )
        
        if cart_item and files:
            try:
                self.file_handler.handle_uploads(
                    cart_item=cart_item,
                    product=product,
                    files=files
                )
            except ValidationError as e:
                raise (f"خطایی رخ داد: {str(e)}")

        return cart_item
    