import logging
from typing import Dict, Any

from django.db import transaction
from rest_framework.exceptions import ValidationError, NotFound

from core.models import CartItem
from core.domain.cart.services import CartDomainService
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
        self._domain_service = CartDomainService()
        self.validator = CartDataValidator()
        
    def update(self, cart_item_id: int, raw_data: Dict[str, Any]) -> CartItem:
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
        
        # ===== دریافت آیتم ===== #
        current_item = self._domain_service._item_repo.get_by_id(cart_item_id, self.user)
        if not current_item:
            logger.error(f"CartItem ID: {cart_item_id} not found for User ID: {self.user.id}")
            raise NotFound("آیتم سبد خرید یافت نشد.")
        
        # ===== اعتبارسنجی داده‌های ورودی ===== #
        validated_data = self.validator.validate(
            product_slug=current_item.product.slug, 
            selections=raw_data
        )
        
        # ===== به روز کردن آیتم ===== #
        updated_item = self._domain_service.update_complex_item(
            user=self.user,
            item_id=cart_item_id,
            quantity=raw_data['quantity'],
            specs={
                'quantity_obj': validated_data['quantity_obj'],
                'material_obj': validated_data['material_obj'],
                'options_objs': validated_data['options_obj'],
                'size_obj': validated_data.get('size_obj'),
                'custom_dimensions': validated_data.get('custom_dimensions'),
                'raw_selections': raw_data
            }
        )
        
        return updated_item
        