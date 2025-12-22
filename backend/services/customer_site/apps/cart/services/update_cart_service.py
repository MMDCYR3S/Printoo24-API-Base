import logging
from typing import Dict, Any
from rest_framework.exceptions import ValidationError, NotFound

from core.models import CartItem
from core.cart.services import CartService
from .cart_validator_service import CartDataValidator

logger = logging.getLogger('cart.services.update')

class CartItemUpdateService:
    def __init__(self, user):
        self.user = user
        self.domain_service = CartService()
        self.validator = CartDataValidator()
        
    def update(self, cart_item_id: int, raw_data: Dict[str, Any]) -> CartItem:
        """
        اجرای عملیات بروزرسانی آیتم سبد خرید.
        """
        logger.info(f"Update Item {cart_item_id} for User {self.user.id}")
        
        # 1. دریافت آیتم فعلی (برای گرفتن اسلاگ محصول جهت اعتبارسنجی)
        current_item = self.domain_service._item_repo.get_item_details(cart_item_id, self.user)
        if not current_item:
            raise NotFound("آیتم سبد خرید یافت نشد.")
        
        # 2. اعتبارسنجی مجدد داده‌های جدید
        validated_data = self.validator.validate(
            product_slug=current_item.product.slug, 
            selections=raw_data
        )
        
        # 3. فراخوانی دامین برای آپدیت
        updated_item = self.domain_service.update_complex_item(
            user=self.user,
            item_id=cart_item_id,
            quantity=validated_data['quantity'],
            specs={
                'size_obj': validated_data.get('size_obj'),
                
                # نکته: خروجی Validator کلید option_values دارد
                'option_objs': validated_data['option_values'], 
                
                'custom_dimensions': {
                    'width': validated_data['width'],
                    'height': validated_data['height']
                },
                'has_design': validated_data.get('has_design'),
                'raw_selections': raw_data
            }
        )
        
        logger.info(f"Item {cart_item_id} updated.")
        return updated_item
