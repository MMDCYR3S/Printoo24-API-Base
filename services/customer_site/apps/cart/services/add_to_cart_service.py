from typing import Dict, Any
from decimal import Decimal

from django.db import transaction
from rest_framework.exceptions import ValidationError

from core.models import User, CartItem
from core.common.cart import (
    CartService,
    CartItemService,
    CartRepository,
    CartItemRepository
)
from apps.shop.services import ProductPriceCalculator
from .cart_file_service import FileFinalizeService
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
        self.cart_service = CartService(repository=CartRepository())
        self.cart_item_service = CartItemService(repository=CartItemRepository())
        self.validator = CartDataValidator()
        self.file_finalize = FileFinalizeService()
        
    @transaction.atomic
    def execute(
        self,
        product_slug: str,
        quantity: int,
        selections: Dict[str, Any],
        temp_file_names: Dict[str, str]
    ) -> CartItem:
        """
        نقطه ورود اصلی برای اجرای کامل فرآیند افزودن به سبد خرید.
        این متد به صورت اتمیک اجرا می‌شود.
        """
        
        # ====== اعتبارسنجی داده های ورودی کاربر و محصول ====== #
        validated_data = self.validator.validate(product_slug=product_slug, selections=selections)
        product = validated_data["product"]
        
        # ===== محاسبه قیمت نهایی ===== #
        price_calculator = ProductPriceCalculator(
            product=product,
            quantity=validated_data["quantity_obj"],
            material=validated_data["material_obj"],
            options=validated_data["options_obj"],
            size=validated_data["size_obj"],
            custom_dimensions=validated_data["custom_dimensions"]
        )
        price_detail = price_calculator.calculate()
        final_price_per_unit = Decimal(str(price_detail["final_price"]))
        
        # ===== دریافت سبد خرید یا ایجاد آن برای کاربر ===== #
        cart = self.cart_service.get_or_create_cart_for_user(user=self.user)
        
        # ===== ایجاد آیتم های داخل آیتم سبد خرید ===== #
        item_details = {
            "selections": selections,
            "product_name_snapshot": product.name,
            "price_detail": price_detail,
        }
        
        existing_item = self.cart_item_service.find_item(
            cart=cart,
            product=product,
            items=item_details
        )
        
        # ===== بررسی اینکه آیا محصول از قبل وجود دارد و قرار است آپدیت شود یا خیر ===== #
        if existing_item:
            new_quantity = existing_item.quantity + quantity
            cart_item = self.cart_item_service.update_item_quantity(existing_item, new_quantity)
        else:
            # ===== ایجاد آیتم سبد خرید ===== #
            cart_item = self.cart_item_service.add_item(
                cart=cart,
                product=product,
                quantity=quantity,
                price=final_price_per_unit,
                items=item_details
            )
        
        if cart_item and temp_file_names:
            try:
                self.file_finalize.finalize_uploads(
                    cart_item=cart_item,
                    temp_file_names=temp_file_names
                )
            except ValidationError as e:
                raise e

        return cart_item
    