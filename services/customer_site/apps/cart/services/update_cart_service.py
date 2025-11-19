from typing import Dict, Any, Optional
from decimal import Decimal

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.core.files.uploadedfile import UploadedFile
from rest_framework.exceptions import ValidationError

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
        cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__user=self.user)
        product = cart_item.product
        
        # ===== یافتن ویژگی های انتخاب شده توسط کاربر در سبد خرید ===== #
        quantity_obj = get_object_or_404(ProductQuantity, id=data['quantity_id'])
        material_obj = get_object_or_404(ProductMaterial, id=data['material_id'])
        
        # ===== اعتبارسنجی تعداد محصول که اگر 0 بود، باید حذف شود ===== #
        size_obj = None
        if data.get('size_id'):
            size_obj = get_object_or_404(ProductSize, id=data['size_id'])

        options_objs = []
        if data.get('option_ids'):
            options_objs = list(ProductOption.objects.filter(id__in=data['option_ids']))

        custom_dimensions = None
        if data.get('custom_width') and data.get('custom_height'):
            custom_dimensions = {
                'width': data['custom_width'], 
                'height': data['custom_height']
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
        final_price = price_result['final_price']
        
        # ===== بروزرسانی آیتم سبد خرید ===== #
        cart_item.product_quantity = quantity_obj
        cart_item.product_material = material_obj
        cart_item.product_size = size_obj
        
        # ===== بروزرسانی ابعاد دلخواه(در صورت وجود) ===== #
        if custom_dimensions:
            cart_item.custom_width = custom_dimensions['width']
            cart_item.custom_height = custom_dimensions['height']
        else:
            cart_item.custom_width = None
            cart_item.custom_height = None
            
        cart_item.price = final_price
        cart_item.save()
        
        cart_item.product_options.set(options_objs)
        
        return cart_item
        