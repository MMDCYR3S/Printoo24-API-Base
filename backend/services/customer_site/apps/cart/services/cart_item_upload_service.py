import os
import logging
from typing import Tuple

from django.core.files.base import ContentFile
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied

from core.models import User, CartItem, ProductFileUploadRequirement, CartItemUpload
from core.domain.cart import CartItemRepository
from ..utils.validators import (
    validate_image_cmyk,
    validate_image_dpi,
    validate_image_dimensions,
)

logger = logging.getLogger('cart.services.item_upload')

class CartItemUploadService:
    """
    سرویس آپلود فایل مستقیم برای یک آیتم در سبد خرید.
    """
    def __init__(self):
        self.item_repo = CartItemRepository()

    def upload_file(self, user: User, cart_item_id: int, requirement_id: int, file_obj) -> CartItemUpload:
        
        logger.info(f"Uploading file for CartItem: {cart_item_id}, Req: {requirement_id}")

        # 1. دریافت آیتم و بررسی مالکیت (Security)
        cart_item = self.item_repo.get_item_details(cart_item_id, user)
        if not cart_item:
            raise NotFound("آیتم مورد نظر در سبد خرید یافت نشد.")

        # 2. دریافت نیازمندی فایل (Requirement)
        try:
            requirement = ProductFileUploadRequirement.objects.get(
                id=requirement_id, 
                product=cart_item.product
            )
        except ProductFileUploadRequirement.DoesNotExist:
            raise ValidationError("این نیازمندی فایل برای محصول انتخابی معتبر نیست.")

        # 3. استخراج ابعاد ذخیره شده در آیتم
        # چون در مرحله AddToCart ابعاد دقیق محاسبه و در JSON ذخیره شده است
        try:
            item_details = cart_item.items.get('details', {})
            required_width = float(item_details.get('width', 0))
            required_height = float(item_details.get('height', 0))
            
            if required_width <= 0 or required_height <= 0:
                # فال‌بک: اگر در جیسون نبود (محصولات قدیمی)، دوباره محاسبه کنیم؟ 
                # فعلا خطا می‌دهیم چون دیتای آیتم باید کامل باشد
                raise ValidationError("ابعاد آیتم در سبد خرید مشخص نیست.")
                
        except (AttributeError, ValueError):
            raise ValidationError("دیتای آیتم سبد خرید ناقص است.")

        # 4. اعتبارسنجی فنی فایل (DPI, CMYK, Dimensions)
        self._validate_technical_specs(file_obj, required_width, required_height)

        # 5. حذف فایل قبلی اگر وجود دارد (Replace Logic)
        # اگر کاربر قبلاً برای این Requirement فایلی آپلود کرده، آن را پاک می‌کنیم
        CartItemUpload.objects.filter(cart_item=cart_item, requirement=requirement).delete()

        # 6. ذخیره فایل نهایی
        upload_instance = CartItemUpload.objects.create(
            cart_item=cart_item,
            requirement=requirement,
            file=file_obj
        )
        
        logger.info(f"File uploaded successfully: {upload_instance.id}")
        return upload_instance

    def _validate_technical_specs(self, file, width, height):
        """
        اجرای ولیدیتورهای تخصصی روی فایل در حافظه
        """
        try:
            # 1. ابعاد
            file.seek(0)
            validate_image_dimensions(file, width, height)
            
            # 2. رنگ (CMYK)
            file.seek(0)
            validate_image_cmyk(file)
            
            # 3. کیفیت (DPI)
            file.seek(0)
            validate_image_dpi(file)
            
        except Exception as e:
            logger.warning(f"Technical validation failed: {e}")
            raise ValidationError(detail=str(e))
