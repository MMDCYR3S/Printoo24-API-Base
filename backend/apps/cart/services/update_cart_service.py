import logging
from typing import Dict, Any

from django.db import transaction
from django.db.models import Q
from django.core.exceptions import ValidationError

from apps.cart.models import CartItem
from apps.cart.utils.cart_processor import CartProcessor
from apps.cart.exceptions import ItemNotFoundException
from core.models import User

logger = logging.getLogger('cart.services.update')

class CartItemUpdateService:
    """
    سرویس ویرایش آیتم سبد خرید (پشتیبانی از فرمول‌ساز جدید).
    """
    def __init__(self, user: User = None, session_key: str = None):
        self.user = user if (user and user.is_authenticated) else None
        self.session_key = session_key

        if not self.user and not self.session_key:
            raise ValidationError("شناسه کاربر یا نشست مهمان برای ویرایش الزامی است.")

    def _get_cart_item(self, item_id: int) -> CartItem:
        query = Q(id=item_id)
        if self.user:
            query &= Q(cart__user=self.user)
        else:
            query &= Q(cart__session_key=self.session_key, cart__user__isnull=True)

        try:
            return CartItem.objects.select_related('cart', 'product').get(query)
        except CartItem.DoesNotExist:
            raise ItemNotFoundException("آیتم مورد نظر یافت نشد یا دسترسی غیرمجاز است.")

    @transaction.atomic
    def update(self, cart_item_id: int, selections: Dict[str, Any]) -> CartItem:
        logger.info(f"Updating Item {cart_item_id} (User: {self.user}, Session: {self.session_key})")

        current_item = self._get_cart_item(cart_item_id)

        # 🌟 استفاده از پراسسور جدید که قبلاً نوشتیم (فقط product و selections می‌گیرد)
        processor = CartProcessor(
            product=current_item.product, 
            selections=selections
        ).process()

        cart = current_item.cart

        duplicate_item = CartItem.objects.find_duplicate_item(
            cart=cart,
            product=current_item.product,
            items_data=processor.result_item_data
        )
        
        if duplicate_item and duplicate_item.id != current_item.id:
            logger.info(f"Merge required: Deleting {current_item.id}, Merging into {duplicate_item.id}")
            
            # در صورت ادغام با یک آیتم دیگر، Quantity (ردیف سبد خرید) را جمع می‌زنیم
            duplicate_item.quantity += current_item.quantity 
            
            # قیمت نهایی فرمول ضربدر تعداد ردیف‌ها
            duplicate_item.price = processor.result_price * duplicate_item.quantity 
            duplicate_item.save()
            
            for upload in current_item.uploads.all():
                upload.cart_item = duplicate_item
                upload.save()

            current_item.delete()
            return duplicate_item
            
        else:
            logger.info("In-place update executed")
            current_item.name = processor.result_name
            current_item.description = processor.result_description
            
            # در آپدیتِ درجا (In-place)، تعداد (quantity) همانی می‌ماند که بود، فقط قیمت جدید روی آن اعمال می‌شود
            current_item.price = processor.result_price * current_item.quantity
            current_item.items = processor.result_item_data
            current_item.save()
            
            return current_item
        