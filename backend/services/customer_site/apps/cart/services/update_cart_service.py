import logging
from typing import Dict, Any

from django.db import transaction
from django.core.exceptions import ValidationError

from apps.cart.models import CartItem
from apps.cart.utils.cart_processor import CartProcessor
from apps.cart.exceptions import ItemNotFoundException

logger = logging.getLogger('cart.services.update')

# ========== CART ITEM UPDATE SERVICE ========== #
class CartItemUpdateService:
    def __init__(self, user):
        self.user = user

    @transaction.atomic
    def update(self, cart_item_id: int, raw_data: Dict[str, Any]) -> CartItem:
        logger.info(f"Updating Item {cart_item_id}")

        # ===== دریافت آیتم ===== #
        current_item = CartItem.objects.get_item_details(cart_item_id, self.user)
        if not current_item:
            raise ItemNotFoundException("آیتم یافت نشد.")

        # ===== پردازش اطلاعات ===== #
        quantity_input = int(raw_data.pop('quantity', 1))
        
        processor = CartProcessor(
            product=current_item.product, 
            selections=raw_data, 
            quantity_input=quantity_input
        ).process()

        # ===== افزودن آیتم به سبد خرید ===== #
        cart = current_item.cart
        duplicate_item = CartItem.objects.find_duplicate_item(
            cart=cart,
            product=current_item.product,
            items_data=processor.result_item_data
        )
        
        # ===== بررسی اینکه آیا آیتم تکراری است ===== #
        if duplicate_item and duplicate_item.id != current_item.id:
            logger.info(f"Merge required: Deleting {current_item.id}, Updating {duplicate_item.id}")
            duplicate_item.quantity += processor.result_quantity
            duplicate_item.price = processor.result_price 
            duplicate_item.save()
            
            current_item.delete()
            return duplicate_item
        else:
            # ===== آپدیت آیتم ===== #
            logger.info("In-place update")
            current_item.name = processor.result_name
            current_item.description = processor.result_description
            current_item.quantity = processor.result_quantity
            current_item.price = processor.result_price
            current_item.items = processor.result_item_data
            current_item.save()
            return current_item
