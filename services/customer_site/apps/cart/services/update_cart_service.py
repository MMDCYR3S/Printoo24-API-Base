import logging
from typing import Dict, Any

from django.db import transaction
from rest_framework.exceptions import ValidationError, NotFound

from core.models import CartItem
from apps.shop.services import ProductPriceCalculator
from .cart_validator_service import CartDataValidator

# ===== تعریف لاگر اختصاصی برای سرویس بروزرسانی سبد خرید ===== #
logger = logging.getLogger('cart.services.update')

class CartItemUpdateService:
    """
    سرویس مسئول ویرایش ویژگی‌های محصول در سبد خرید.
    
    این سرویس وظیفه دارد:
    1. آیتم مورد نظر را در سبد خرید کاربر پیدا کند.
    2. داده‌های جدید (سایز، جنس، تیراژ و...) را اعتبارسنجی کند.
    3. قیمت جدید را محاسبه نماید.
    4. اطلاعات آیتم را در دیتابیس بروزرسانی کند.
    """

    def __init__(self, user):
        self.user = user
        # ===== تزریق وابستگی اعتبارسنج ===== #
        self.validator = CartDataValidator()
        
    @transaction.atomic
    def update(self, cart_item_id: int, data: Dict[str, Any]) -> CartItem:
        """
        اجرای عملیات بروزرسانی آیتم سبد خرید.

        Args:
            cart_item_id (int): شناسه آیتم سبد خرید.
            data (dict): دیکشنری داده‌های جدید (شامل quantity_id, material_id, ...).

        Returns:
            CartItem: آیتم بروزرسانی شده.

        Raises:
            NotFound: اگر آیتم یافت نشود.
            ValidationError: اگر داده‌ها نامعتبر باشند.
        """
        logger.info(f"Request to update CartItem ID: {cart_item_id} for User ID: {self.user.id}")
        
        # ===== دریافت آیتم سبد خرید با بررسی مالکیت ===== #
        try:
            cart_item = CartItem.objects.select_related('product').get(id=cart_item_id, cart__user=self.user)
        except CartItem.DoesNotExist:
            logger.warning(f"CartItem {cart_item_id} not found for User ID: {self.user.id}")
            raise NotFound("آیتم مورد نظر در سبد خرید شما یافت نشد.")
        
        product = cart_item.product
        
        try:
            # ===== اعتبارسنجی داده‌های جدید با استفاده از Validator ===== #
            # نکته: استفاده از Validator مرکزی برای جلوگیری از تکرار کد منطقی
            validated_data = self.validator.validate(product_slug=product.slug, selections=data)
            
            logger.debug(f"Data validation passed for CartItem ID: {cart_item_id}")

            # ===== استخراج آبجکت‌های معتبر شده ===== #
            quantity_obj = validated_data["quantity_obj"]
            material_obj = validated_data["material_obj"]
            size_obj = validated_data["size_obj"]
            options_objs = validated_data["options_obj"]
            custom_dimensions = validated_data["custom_dimensions"]

            # ===== محاسبه قیمت جدید ===== #
            calculator = ProductPriceCalculator(
                product=product,
                quantity=quantity_obj,
                material=material_obj,
                options=options_objs,
                size=size_obj,
                custom_dimensions=custom_dimensions
            )
            
            price_result = calculator.calculate()
            final_price = price_result["final_price"]
            
            logger.debug(f"New price calculated: {final_price}")

            # ===== آماده‌سازی داده‌ها برای ذخیره در JSON Field ===== #
            # ساختار item_details باید با ساختار AddToCart یکسان باشد
            item_details = {
                "selections": {
                    "quantity_id": quantity_obj.id,
                    "material_id": material_obj.id,
                    "size_id": size_obj.id if size_obj else None,
                    "options_ids": [opt.id for opt in options_objs], # توجه: نام فیلد باید یکسان باشد
                    "custom_dimensions": custom_dimensions,
                },
                "product_name_snapshot": product.name,
                "price_detail": price_result,
            }
            
            # ===== بروزرسانی تعداد (Quantity) خود آیتم ===== #
            if 'quantity' in data:
                new_quantity = data['quantity']
                if not isinstance(new_quantity, int) or new_quantity <= 0:
                    raise ValidationError({"quantity": "تعداد باید یک عدد صحیح بزرگتر از صفر باشد."})
                cart_item.quantity = new_quantity

            # ===== اعمال تغییرات نهایی روی آیتم ===== #
            cart_item.items = item_details
            cart_item.price = final_price
            
            cart_item.save(update_fields=['items', 'price', 'quantity', 'updated_at'])
            
            logger.info(f"CartItem ID: {cart_item_id} updated successfully.")
            return cart_item

        except ValidationError as e:
            logger.warning(f"Validation failed during update: {e}")
            raise e
        except Exception as e:
            logger.exception(f"Unexpected error updating CartItem ID: {cart_item_id}")
            raise ValidationError("خطای سیستمی در بروزرسانی سبد خرید.")
