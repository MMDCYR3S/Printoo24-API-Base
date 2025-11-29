import logging
from typing import Dict, Any
from decimal import Decimal

from django.db import transaction
from rest_framework.exceptions import ValidationError

from core.models import User, CartItem
from core.domain.cart.services import CartDomainService 

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
        self.domain_service = CartDomainService()
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
        logger.info(f"Adding product {product_slug} to cart for user {self.user.id}")
        
        try:
            # ===== اعتبارسنجی داده‌های ورودی کاربر و محصول ===== #
            validated_data = self.validator.validate(
                product_slug=product_slug, 
                selections=selections
            )
            product = validated_data["product"]
            logger.debug(f"Validation successful for Product: {product.name}")
            
            # ===== آماده‌سازی مسیرهای نهایی فایل‌های آپلود شده ===== #
            final_file_paths = {}
            if temp_file_names:
                final_file_paths = self.file_finalize.finalize_files(
                    temp_file_names, 
                    user_id=self.user.id
                )
            
            # ===== افزودن آیتم به سبد خرید ===== #
            cart_item = self.domain_service.add_complex_item(
                user=self.user,
                product=product,
                quantity=quantity,
                specs={
                    'quantity_obj': validated_data['quantity_obj'],
                    'material_obj': validated_data['material_obj'],
                    'options_objs': validated_data['options_obj'],
                    'size_obj': validated_data.get('size_obj'),
                    'custom_dimensions': validated_data.get('custom_dimensions'),
                    'raw_selections': selections
                },
                uploaded_files_map=final_file_paths
            )
            
            logger.info(f"CartItem created successfully: {cart_item.id}")
            return cart_item
        # ===== مدیریت استثناها و لاگینگ ===== #
        except Exception as e:
            logger.error(f"Add to cart failed: {e}")
            raise e
