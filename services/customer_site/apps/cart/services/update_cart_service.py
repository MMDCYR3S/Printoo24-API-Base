from typing import Dict, Any, Optional
from decimal import Decimal

from django.db import transaction
from django.core.files.uploadedfile import UploadedFile
from rest_framework.exceptions import ValidationError

from core.models import User, CartItem
from core.common.cart import CartItemService, CartItemRepository
from apps.shop.services import ProductPriceCalculator
from .cart_file_service import FileFinalizeService
from .cart_validator_service import CartDataValidator

# ===== Update Cart Item Service ===== #
class UpdateCartItemService:
    """
    سرویسی اختصاصی برای ویرایش یک آیتم موجود در سبد خرید (مانند تغییر تعداد).
    این سرویس هیچ ارتباطی با فرآیند آپلود فایل ندارد.
    """
    
    def __init__(self, user: User):
        self.user = user
        self.cart_item_service = CartItemService(repository=CartItemRepository)
        
    def update(self, cart_item_id: int, quantity: int) -> CartItem:
        """
        تعداد یک آیتم مشخص در سبد خرید کاربر را به‌روزرسانی می‌کند.
        """
        
        # ===== دریافت سبد خرید کاربر و آیتم مورد نظر ===== #
        cart_item = CartItem.objects.get(id=cart_item_id, cart__user=self.user)
        
        # ===== اعتبارسنجی تعداد محصول که اگر 0 بود، باید حذف شود ===== #
        if quantity < 0:
            self.cart_item_service.remove_item(item=cart_item)
            
        # ===== پیدا کردن سبد خرید کاربر برای ویرایش ===== #
        try:
            cart_item
        except CartItem.DoesNotExist:
            raise ValidationError("آیتم مورد نظر در سبد خرید شما یافت نشد.")
        
        updated_item = self.cart_item_service.update_item_quantity(cart_item, quantity)
        
        return updated_item
        
        
        