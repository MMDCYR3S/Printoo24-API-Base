from typing import Dict, Any, Optional
from decimal import Decimal

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.core.files.uploadedfile import UploadedFile
from rest_framework.exceptions import ValidationError, NotFound

from core.models import (
    User,
    CartItem,
    ProductSize,
    ProductMaterial,
    ProductOption,
    ProductQuantity,
    OptionValue
)
from core.common.cart import CartItemService, CartItemRepository
from apps.shop.services import ProductPriceCalculator
from .cart_file_service import FileFinalizeService
from .cart_validator_service import CartDataValidator

# ===== Update Cart Item Service ===== #
class CartItemUpdateService:
    """
    سرویس مسئول ویرایش ویژگی‌های محصول (جنس، سایز، تیراژ، آپشن) در سبد خرید
    و محاسبه مجدد قیمت با استفاده از ProductPriceCalculator.
    """

    def __init__(self, user):
        self.user = user
        
    @transaction.atomic
    def update(self, cart_item_id: int, data: dict) -> CartItem:
        """
        :param cart_item_id: شناسه آیتم
        :param validated_data: دیکشنری داده‌های تمیز شده از سریالایزر
        """
        
        # ===== دریافت سبد خرید کاربر و آیتم مورد نظر ===== #
        try:
            cart_item = CartItem.objects.select_related('product').get(id=cart_item_id, cart__user=self.user)
        except CartItem.DoesNotExist:
            raise NotFound("آیتم مورد نظر در سبد خرید شما یافت نشد.")
        
        product = cart_item.product
        
        # ===== یافتن ویژگی های انتخاب شده توسط کاربر در سبد خرید ===== #
        quantity_obj = get_object_or_404(ProductQuantity, id=data["quantity_id"])
        material_obj = get_object_or_404(ProductMaterial, id=data["material_id"])
        
        # ===== اعتبارسنجی تعداد محصول که اگر 0 بود، باید حذف شود ===== #
        size_obj = None
        if data.get("size_id"):
            size_obj = get_object_or_404(ProductSize, id=data["size_id"])

        options_objs = []
        if data.get("option_ids"):
            options_objs = list(ProductOption.objects.filter(id__in=data["option_ids"]))
            if len(options_objs) != len(data["option_ids"]):
                raise ValidationError("یک یا چند آپشن برای این محصول معتبر نیستند.")
            
        custom_dimensions = None
        if data.get("custom_width") and data.get("custom_height"):
            custom_dimensions = {
                "width": data["custom_width"], 
                "height": data["custom_height"]
            }
        
        # ===== اعتبارسنجی ویژگی ها ===== #
        if quantity_obj.product_id != product.id:
            raise ValidationError("این تیراژ برای محصول انتخابی معتبر نیست.")
            
        if material_obj.product_id != product.id:
            raise ValidationError("این متریال برای محصول انتخابی معتبر نیست.")
            
        if size_obj and size_obj.product_id != product.id:
            raise ValidationError("این سایز برای محصول انتخابی معتبر نیست.")
        
        # ===== بررسی ویژگی های منحصر به فرد ===== #
        for opt in options_objs:
            if opt.product_id != product.id:
                raise ValidationError(f"آپشن {opt.name} برای این محصول معتبر نیست.")

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
        
        # ===== بروزرسانی آیتم سبد خرید ===== #
        updated_items = {
            "quantity_id": quantity_obj.id,
            "material_id": material_obj.id,
            "size_id": size_obj.id if size_obj else None,
            "option_ids": [opt.id for opt in options_objs],
            "custom_width": custom_dimensions.get("width") if custom_dimensions else None,
            "custom_height": custom_dimensions.get("height") if custom_dimensions else None,
        }
        
        # ===== بررسی تیراژ مربوط به آیتم ===== #
        if 'quantity' in data:
            new_quantity = data['quantity']
            if not isinstance(new_quantity, int) or new_quantity <= 0:
                raise ValidationError({"quantity": "تعداد باید یک عدد صحیح بزرگتر از صفر باشد."})
            cart_item.quantity = new_quantity
        
        # ===== بروزرسانی ابعاد دلخواه(در صورت وجود) ===== #
        cart_item.items = updated_items
        cart_item.price = final_price
        cart_item.save(update_fields=['items', 'price', 'quantity', 'updated_at'])
        
        return cart_item
        