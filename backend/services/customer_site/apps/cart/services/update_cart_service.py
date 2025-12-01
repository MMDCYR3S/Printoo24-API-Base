import logging
from typing import Dict, Any

from django.db import transaction
from rest_framework.exceptions import ValidationError, NotFound

from core.models import CartItem
from core.domain.cart.services import CartDomainService
from .cart_validator_service import CartDataValidator

# ===== تعریف لاگر اختصاصی ===== #
logger = logging.getLogger('cart.services.update')

class CartItemUpdateService:
    def __init__(self, user):
        self.user = user
        self._domain_service = CartDomainService()
        self.validator = CartDataValidator()
        
    def update(self, cart_item_id: int, raw_data: Dict[str, Any]) -> CartItem:
        """
        اجرای عملیات بروزرسانی آیتم سبد خرید.
        """
        logger.info(f"Request to update CartItem ID: {cart_item_id} for User ID: {self.user.id}")
        
        # ===== اطمینان از وجود آیتم ===== #
        current_item = self._domain_service._item_repo.get_item_details(cart_item_id, self.user)
        
        if not current_item:
            logger.error(f"CartItem ID: {cart_item_id} not found/access denied for User ID: {self.user.id}")
            raise NotFound("آیتم سبد خرید یافت نشد.")
        
        # ===== اعتبارسنجی ===== #
        validated_data = self.validator.validate(
            product_slug=current_item.product.slug, 
            selections=raw_data
        )
        
        # ===== به روز رسانی ===== #
        updated_item = self._domain_service.update_complex_item(
            user=self.user,
            item_id=cart_item_id,
            quantity=validated_data['quantity'],
            specs={
                'material_obj': validated_data['material_obj'],
                'size_obj': validated_data.get('size_obj'),
                'option_objs': validated_data['options_obj'],
                'custom_dimensions': validated_data.get('custom_dimensions'),
                'has_design': validated_data.get('has_design'),
                'raw_selections': raw_data
            }
        )
        
        logger.info(f"CartItem {cart_item_id} updated successfully.")
        return updated_item
