import logging
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

# ===== تعریف لاگر اختصاصی برای سرویس افزودن به سبد خرید ===== #
logger = logging.getLogger('cart.services.add_to_cart')

class AddToCartService:
    """
    سرویس مدیریت فرآیند افزودن محصول به سبد خرید.
    
    این کلاس به عنوان یک Facade یا Orchestrator عمل می‌کند و وظیفه دارد
    تا با هماهنگی بین سرویس‌های اعتبارسنجی، محاسبه قیمت، فایل‌ها و دیتابیس،
    یک محصول را به سبد خرید کاربر اضافه کند یا اگر وجود دارد، تعداد آن را بروزرسانی کند.
    
    وظایف اصلی:
    1. اعتبارسنجی انتخاب‌های کاربر (رنگ، سایز و...).
    2. محاسبه دقیق قیمت بر اساس ویژگی‌های انتخابی.
    3. مدیریت سبد خرید (ایجاد یا بازیابی).
    4. مدیریت آیتم تکراری (Merge Logic).
    5. نهایی‌سازی فایل‌های آپلود شده موقت.
    """
    
    def __init__(self, user: User):
        self.user = user
        # ===== تزریق وابستگی‌های لازم ===== #
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
        اجرای منطق افزودن به سبد خرید به صورت اتمیک.

        Args:
            product_slug (str): اسلاگ محصول مورد نظر.
            quantity (int): تعداد درخواستی کاربر.
            selections (Dict[str, Any]): ویژگی‌های انتخابی (سایز، متریال، آپشن‌ها).
            temp_file_names (Dict[str, str]): دیکشنری نام فایل‌های موقت آپلود شده.

        Returns:
            CartItem: آبجکت آیتم سبد خرید (جدید یا آپدیت شده).

        Raises:
            ValidationError: در صورت عدم اعتبار داده‌ها یا مشکل در پردازش فایل.
        """
        logger.info(f"Starting AddToCart process for User ID: {self.user.id}, Product Slug: {product_slug}")
        
        try:
            # ===== اعتبارسنجی داده‌های ورودی کاربر و محصول ===== #
            validated_data = self.validator.validate(product_slug=product_slug, selections=selections)
            product = validated_data["product"]
            logger.debug(f"Validation successful for Product: {product.name}")
            
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
            
            logger.debug(f"Price calculated: {final_price_per_unit} per unit.")
            
            # ===== دریافت سبد خرید یا ایجاد آن برای کاربر ===== #
            cart = self.cart_service.get_or_create_cart_for_user(user=self.user)
            
            # ===== آماده‌سازی جزئیات آیتم برای ذخیره در دیتابیس ===== #
            item_details = {
                "selections": selections,
                "product_name_snapshot": product.name,
                "price_detail": price_detail,
            }
            
            # ===== جستجو برای آیتم مشابه در سبد خرید ===== #
            existing_item = self.cart_item_service.find_item(
                cart=cart,
                product=product,
                items=item_details
            )
            
            # ===== بررسی اینکه آیا محصول از قبل وجود دارد و قرار است آپدیت شود یا خیر ===== #
            if existing_item:
                logger.info(f"Item exists in cart. Updating quantity for Item ID: {existing_item.id}")
                new_quantity = existing_item.quantity + quantity
                cart_item = self.cart_item_service.update_item_quantity(existing_item, new_quantity)
            else:
                logger.info("Creating new cart item.")
                # ===== ایجاد آیتم سبد خرید جدید ===== #
                cart_item = self.cart_item_service.add_item(
                    cart=cart,
                    product=product,
                    quantity=quantity,
                    price=final_price_per_unit,
                    items=item_details
                )
            
            # ===== پردازش و نهایی‌سازی فایل‌های آپلود شده ===== #
            if cart_item and temp_file_names:
                try:
                    logger.info(f"Processing {len(temp_file_names)} temp files for CartItem ID: {cart_item.id}")
                    self.file_finalize.finalize_uploads(
                        cart_item=cart_item,
                        temp_file_names=temp_file_names
                    )
                except ValidationError as e:
                    logger.error(f"File finalization failed for CartItem ID: {cart_item.id}. Error: {e}")
                    raise e

            logger.info(f"AddToCart executed successfully. CartItem ID: {cart_item.id}")
            return cart_item

        except Exception as e:
            if not isinstance(e, ValidationError):
                logger.exception(f"Unexpected error in AddToCart for User ID: {self.user.id}")
            raise e
