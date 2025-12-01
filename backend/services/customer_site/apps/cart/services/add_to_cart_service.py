import logging
from typing import Dict, Any

from django.db import transaction
from rest_framework.exceptions import ValidationError

from core.models import User, CartItem
from core.domain.cart.services import CartDomainService 

from .cart_file_service import FileFinalizeService 
from .cart_validator_service import CartDataValidator

# ===== تعریف لاگر اختصاصی ===== #
logger = logging.getLogger('cart.services.add_to_cart')

class AddToCartService:
    def __init__(self, user: User):
        self.user = user
        self.domain_service = CartDomainService()
        self.validator = CartDataValidator()
        self.file_finalize = FileFinalizeService()
        
    @transaction.atomic
    def execute(
        self,
        product_slug: str,
        selections: Dict[str, Any],
        temp_file_names: Dict[str, str]
    ) -> CartItem:
        """
        اجرای منطق افزودن به سبد خرید.
        """
        logger.info(f"Adding product {product_slug} to cart for user {self.user.id}")
        
        try:
            # ===== اعتبارسنجی داده‌های ورودی ===== #
            validated_data = self.validator.validate(
                product_slug=product_slug, 
                selections=selections
            )
            
            product = validated_data["product"]
            quantity = validated_data["quantity"] # الان int است
            
            logger.debug(f"Validation successful for Product: {product.name}")
            
            # ===== نهایی‌سازی فایل‌ها ===== #
            final_file_paths = {}
            if temp_file_names:
                final_file_paths = self.file_finalize.finalize_files(
                    temp_file_names, 
                    user_id=self.user.id
                )
                
            has_design = validated_data.get('has_design')
            if has_design and final_file_paths == {}:
                raise ValidationError("لطفاً فایل های طراحی خود را آپلود کنید.") 
            
            # ===== افزودن آیتم به سبد خرید (فراخوانی Domain Service) ===== #
            cart_item = self.domain_service.add_complex_item(
                user=self.user,
                product=product,
                quantity=quantity,
                specs={
                    # دیگر quantity_obj نداریم
                    'material_obj': validated_data['material_obj'],
                    'size_obj': validated_data.get('size_obj'),
                    'option_objs': validated_data['options_obj'],
                    'custom_dimensions': validated_data.get('custom_dimensions'),
                    'has_design': validated_data.get('has_design'),
                    
                    # ذخیره انتخاب‌های خام برای بازگرداندن در فرانت (Re-populate)
                    'raw_selections': selections 
                },
                uploaded_files_map=final_file_paths
            )
            
            logger.info(f"CartItem created successfully: {cart_item.id}")
            return cart_item

        except Exception as e:
            logger.error(f"Add to cart failed: {e}")
            raise e
