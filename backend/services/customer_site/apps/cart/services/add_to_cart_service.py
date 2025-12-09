import logging
from typing import Dict, Any
from django.db import transaction
from core.models import User, CartItem
from core.domain.commerce.cart.services import CartDomainService 
from .cart_validator_service import CartDataValidator

logger = logging.getLogger('cart.services.add_to_cart')

class AddToCartService:
    def __init__(self, user: User):
        self.user = user
        self.domain_service = CartDomainService()
        self.validator = CartDataValidator()
        
    @transaction.atomic
    def execute(self, product_slug: str, selections: Dict[str, Any]) -> CartItem:
        """
        اجرای منطق افزودن به سبد خرید (بدون آپلود فایل).
        فایل‌ها در مرحله بعد و توسط سرویس دیگری آپلود می‌شوند.
        """
        logger.info(f"Adding product {product_slug} to cart for user {self.user.id}")
        
        try:
            # 1. اعتبارسنجی داده‌های محصول و آپشن‌ها
            validated_data = self.validator.validate(
                product_slug=product_slug, 
                selections=selections
            )
            
            # نکته: اینجا دیگر چک نمی‌کنیم که فایل آپلود شده یا نه.
            # وضعیت آیتم در سبد خرید می‌تواند "Incomplete" باشد (در لاجیک‌های بعدی)
            
            # 2. افزودن آیتم به سبد خرید
            cart_item = self.domain_service.add_complex_item(
                user=self.user,
                product=validated_data["product"],
                quantity=validated_data["quantity"],
                specs={
                    'size_obj': validated_data.get('size_obj'),
                    'option_objs': validated_data['option_values'],
                    'width': validated_data["width"],
                    'height': validated_data["height"],
                    'has_design': validated_data.get('has_design'),
                    'raw_selections': selections
                }
            )
            
            logger.info(f"CartItem created successfully: {cart_item.id}")
            return cart_item

        except Exception as e:
            logger.error(f"Add to cart failed: {e}")
            raise e
